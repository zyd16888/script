package main

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/PaulSonOfLars/gotgbot/v2"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"log"
	"math"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"gopkg.in/yaml.v2"
)

type Config struct {
	MongoURI         string `yaml:"mongo_uri"`
	DatabaseName     string `yaml:"database_name"`
	CollectionName   string `yaml:"collection_name"`
	TelegramBotToken string `yaml:"telegram_bot_token"`
	ChatID           int64  `yaml:"chat_id"`
	KeepDays         int    `yaml:"keep_days"`
	ImageProxyURL    string `yaml:"image_proxy_url"`
}

type AppState struct {
	SentItems map[string][]string `json:"sent_items"`
	QueryDate string              `json:"query_date"`
}

var (
	config       Config
	appState     AppState
	collection   *mongo.Collection
	bot          *gotgbot.Bot
	queryDateBak string
)

const (
	configFile          = "config.yaml"
	appStateFile        = "app_state.json"
	markdownEscapeChars = "_*[]()~`>#+-=|{}.!"
)

func init() {
	loadConfig()
	loadAppState()
	initMongoDB()
	initTelegramBot()
}

func loadConfig() {
	data, err := os.ReadFile(configFile)
	if err != nil {
		log.Fatalf("Error reading config file: %v", err)
	}

	err = yaml.Unmarshal(data, &config)
	if err != nil {
		log.Fatalf("Error parsing config file: %v", err)
	}
	// 直接使用 config.ChatID，因为它已经是 int64 类型
}

func loadAppState() {
	data, err := os.ReadFile(appStateFile)
	if err != nil {
		if os.IsNotExist(err) {
			appState = AppState{
				SentItems: make(map[string][]string),
				QueryDate: "",
			}
			return
		}
		log.Fatalf("Error reading app state file: %v", err)
	}

	err = json.Unmarshal(data, &appState)
	if err != nil {
		log.Fatalf("Error parsing app state file: %v", err)
	}

	queryDateBak = appState.QueryDate

	// If QueryDate is empty, set it to today's date
	if appState.QueryDate == "" {
		appState.QueryDate = time.Now().Format("2006-01-02")
	}
}

func saveAppState() {
	// Create a temporary state without the QueryDate
	tempState := AppState{
		SentItems: appState.SentItems,
		QueryDate: queryDateBak, // Set to empty string when saving
	}

	data, err := json.MarshalIndent(tempState, "", "  ")
	if err != nil {
		log.Printf("Error marshaling app state: %v", err)
		return
	}

	err = os.WriteFile(appStateFile, data, 0644)
	if err != nil {
		log.Printf("Error writing app state file: %v", err)
	}
}

func initMongoDB() {
	clientOptions := options.Client().ApplyURI(config.MongoURI)
	client, err := mongo.Connect(context.TODO(), clientOptions)
	if err != nil {
		log.Fatalf("Error connecting to MongoDB: %v", err)
	}

	err = client.Ping(context.TODO(), nil)
	if err != nil {
		log.Fatalf("Error pinging MongoDB: %v", err)
	}

	collection = client.Database(config.DatabaseName).Collection(config.CollectionName)
}

func initTelegramBot() {
	var err error
	bot, err = gotgbot.NewBot(config.TelegramBotToken, nil)
	if err != nil {
		log.Fatalf("Error creating Telegram bot: %v", err)
	}
}

func escapeMarkdown(text string) string {
	for _, char := range markdownEscapeChars {
		text = strings.ReplaceAll(text, string(char), "\\"+string(char))
	}
	return text
}

func replaceImageURL(imageURL string) string {
	pattern := regexp.MustCompile(`(https?://)([^/]+)/tupian`)
	return pattern.ReplaceAllString(imageURL, config.ImageProxyURL+"/tupian")
}

func sendTelegramMessage(content string, imageList []string) bool {
	maxRetries := 5
	baseDelay := time.Second

	var err error
	for attempt := 0; attempt < maxRetries; attempt++ {
		if len(imageList) == 0 {
			_, err = bot.SendMessage(config.ChatID, content, &gotgbot.SendMessageOpts{
				ParseMode: "MarkdownV2",
			})
		} else {
			media := make([]gotgbot.InputMedia, len(imageList))
			for i, img := range imageList {
				url := replaceImageURL(img)

				photoConfig := gotgbot.InputMediaPhoto{
					Media: gotgbot.InputFileByURL(url),
				}
				if i == len(imageList)-1 {
					photoConfig.Caption = content
					photoConfig.ParseMode = "MarkdownV2"
				}
				media[i] = &photoConfig
			}
			_, err = bot.SendMediaGroup(config.ChatID, media, &gotgbot.SendMediaGroupOpts{
				DisableNotification: true,
			})
			time.Sleep(1 * time.Second)
		}

		if err == nil {
			return true
		}

		if strings.Contains(err.Error(), "Too Many Requests") {
			retryAfter := extractRetryAfter(err.Error())
			log.Printf("API限速，需要等待的时间为： %v 秒", retryAfter)
			if retryAfter > 0 {
				time.Sleep(time.Duration(retryAfter) * time.Second)
			} else {
				delay := time.Duration(math.Pow(2, float64(attempt))) * baseDelay
				time.Sleep(delay)
			}
		} else {
			log.Printf("Error sending message: %v", err)
			return false
		}
	}

	log.Printf("Failed to send message after %d attempts", maxRetries)
	return false
}

func extractRetryAfter(errorMsg string) int {
	// 从错误消息中提取 "retry after" 的值
	// 这里需要根据实际的错误消息格式来实现
	// 例如：如果错误消息格式是 "Too Many Requests: retry after 25"
	parts := strings.Split(errorMsg, "retry after ")
	if len(parts) == 2 {
		retryAfter, err := strconv.Atoi(strings.TrimSpace(parts[1]))
		if err == nil {
			return retryAfter
		}
	}
	return 0
}

func queryAndNotify() int {
	cleanOldData()

	filter := bson.M{"date": appState.QueryDate}
	options := options.Find().SetSort(bson.D{{Key: "post_time", Value: -1}})
	cursor, err := collection.Find(context.TODO(), filter, options)
	if err != nil {
		log.Printf("Error querying MongoDB: %v", err)
		return 0
	}
	defer cursor.Close(context.TODO())

	sentCount := 0
	for cursor.Next(context.TODO()) {
		var doc bson.M
		err := cursor.Decode(&doc)
		if err != nil {
			log.Printf("Error decoding document: %v", err)
			continue
		}

		// 正确处理 _id 字段
		var docID string
		if oid, ok := doc["_id"].(primitive.ObjectID); ok {
			docID = oid.Hex()
		} else {
			log.Printf("Error: _id is not of type ObjectID")
			continue
		}

		if !contains(appState.SentItems[appState.QueryDate], docID) {
			content := fmt.Sprintf("*日期:* %s\n", escapeMarkdown(doc["date"].(string)))
			content += fmt.Sprintf("*标题:* %s\n", escapeMarkdown(doc["title"].(string)))
			content += fmt.Sprintf("*发布时间:* %s\n", escapeMarkdown(doc["post_time"].(string)))
			content += fmt.Sprintf("*番号:* %s\n", escapeMarkdown(doc["number"].(string)))

			if magnet, ok := doc["magnet"].(string); ok && magnet != "" {
				content += fmt.Sprintf("*磁力链接:* `%s`\n", escapeMarkdown(magnet))
			}

			images := make([]string, 0)
			if imgSlice, ok := doc["img"].(primitive.A); ok {
				for _, v := range imgSlice {
					if imgStr, ok := v.(string); ok {
						images = append(images, imgStr)
					}
				}
			} else if imgSlice, ok := doc["img"].([]string); ok {
				images = append(images, imgSlice...)
			} else {
				log.Printf("Error: img field is not of expected type")
			}

			if sendTelegramMessage(content, images) {
				log.Printf(" %s 发送成功\n", doc["number"].(string))
				appState.SentItems[appState.QueryDate] = append(appState.SentItems[appState.QueryDate], docID)
				sentCount++
			} else {
				log.Printf("Unable to send message, ID: %s", docID)
			}
		}
	}

	saveAppState()
	return sentCount
}

func cleanOldData() {
	today := time.Now()
	for date := range appState.SentItems {
		parsedDate, err := time.Parse("2006-01-02", date)
		if err != nil {
			log.Printf("Error parsing date: %v", err)
			continue
		}
		if today.Sub(parsedDate).Hours() > float64(config.KeepDays*24) {
			delete(appState.SentItems, date)
		}
	}
}

func contains(slice []string, item string) bool {
	for _, v := range slice {
		if v == item {
			return true
		}
	}
	return false
}

func setQueryDate(date string) {
	appState.QueryDate = date
	saveAppState()
	log.Printf("Query date set to: %s", date)
}

func main() {
	if len(os.Args) > 1 {
		setQueryDate(os.Args[1])
	} else {
		sentCount := queryAndNotify()
		log.Printf("Sent %d new notifications", sentCount)
	}
}
