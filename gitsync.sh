#!/bin/bash

# 设置存储库列表
REPOS=(
    "https://github.com/yuebinliu/YueChan-Live.git"
    "https://github.com/YanG-1989/m3u.git"
    "https://github.com/iptv-org/awesome-iptv.git"
    "https://github.com/fenxp/iptv.git"
    "https://github.com/gaotianliuyun/gao.git"
    "https://github.com/Meroser/IPTV.git"
    "https://github.com/qist/tvbox.git"
)

# 设置存储库别名
declare -A REPO_ALIASES
REPO_ALIASES["https://github.com/yuebinliu/YueChan-Live.git"]="yuechan-live"
REPO_ALIASES["https://github.com/YanG-1989/m3u.git"]="yang-m3u"
REPO_ALIASES["https://github.com/iptv-org/awesome-iptv.git"]="awesome-iptv"
REPO_ALIASES["https://github.com/fenxp/iptv.git"]="fenxp-iptv"
REPO_ALIASES["https://github.com/gaotianliuyun/gao.git"]="gao-iptv"
REPO_ALIASES["https://github.com/Meroser/IPTV.git"]="meroser-iptv"
REPO_ALIASES["https://github.com/qist/tvbox.git"]="qist-tvbox"

# 本地存储目录
BASE_DIR="/root/syncGitUpx/git_repos"
TEMP_DIR="/root/syncGitUpx/temp_sync"
LOG_FILE="/root/syncGitUpx/gitsync.log"

# 又拍云存储路径映射
declare -A REMOTE_PATHS
REMOTE_PATHS["yang-m3u"]="/YanG-1989/"
REMOTE_PATHS["yuechan-live"]="/YueChan-Live/"
REMOTE_PATHS["awesome-iptv"]="/awesome-iptv/"
REMOTE_PATHS["fenxp-iptv"]="/fenxp-iptv/"
REMOTE_PATHS["fenxp-iptv-dist"]="/fenxp-iptv-dist/"
REMOTE_PATHS["gao-iptv"]="/gao/"
REMOTE_PATHS["meroser-iptv"]="/Meroser-IPTV/"
REMOTE_PATHS["qist-tvbox"]="/qist-tvbox/"

# UPX 认证信息
UPX_AUTH="wYj9DMjVEgnVBMzPzYiSiNP4zciSiNP4zde4mJeXndeYmYjD"

# 创建存储目录
mkdir -p "$BASE_DIR"
mkdir -p "$TEMP_DIR"

# 记录日志
exec > >(tee -a "$LOG_FILE") 2>&1

echo "========== $(date) 开始同步 =========="

# 拉取或更新代码
for REPO in "${REPOS[@]}"; do
    REPO_ALIAS="${REPO_ALIASES[$REPO]}"
    LOCAL_PATH="$BASE_DIR/$REPO_ALIAS"
    SYNC_PATH="$TEMP_DIR/$REPO_ALIAS"
    
    if [ -d "$LOCAL_PATH/.git" ]; then
        echo "Updating $REPO_ALIAS"
        git -C "$LOCAL_PATH" pull
    else
        echo "Cloning $REPO_ALIAS"
        git clone "$REPO" "$LOCAL_PATH"
    fi
    
    # 复制文件并排除 .git 目录
    rsync -av --exclude=".git" "$LOCAL_PATH/" "$SYNC_PATH/"
    
    # 处理分支同步
    if [ "$REPO" == "https://github.com/fenxp/iptv.git" ]; then
        echo "Checking out dist branch for $REPO_ALIAS"
        git -C "$LOCAL_PATH" checkout dist
        rsync -av --exclude=".git" "$LOCAL_PATH/" "$TEMP_DIR/${REPO_ALIAS}-dist/"
        upx --auth="$UPX_AUTH" sync "$TEMP_DIR/${REPO_ALIAS}-dist" "${REMOTE_PATHS["fenxp-iptv-dist"]}"
        rm -rf "$TEMP_DIR/${REPO_ALIAS}-dist"
        git -C "$LOCAL_PATH" checkout master
    fi
    
    # 同步到又拍云
    upx --auth="$UPX_AUTH" sync "$SYNC_PATH" "${REMOTE_PATHS[$REPO_ALIAS]}"
    
    # 清理临时目录
    rm -rf "$SYNC_PATH"
done

echo "========== $(date) 同步完成 =========="
