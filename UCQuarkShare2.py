import requests


class File:
    def __init__(self, auth_info, file_info):
        self._auth = auth_info
        for k, v in auth_info.items():
            setattr(self, "_" + k, v)
        for k, v in file_info.items():
            setattr(self, k, v)

    def __str__(self):
        return self.file_name

    def list(self, pdir_fid=None):
        if pdir_fid is None:
            if not self.dir:
                raise Exception("文件夹才有下一级")
            pdir_fid = self.fid
        resp = requests.get(
            f"{self._url_prefix}/detail",
            params={
                "pwd_id": self._share_id,
                "passcode": self._code,
                "stoken": self._stoken,
                "pdir_fid": pdir_fid,
                "_page": 1,
                "_size": 100000,
            },
        )
        print(f"share id [{self._share_id}] 的同级目录有：")
        for index, i in enumerate(resp.json()["data"]["list"]):
            name = i["file_name"]
            print(f"索引: {index},  name: {name}")

        return [File(self._auth, i) for i in resp.json()["data"]["list"]]

    def save(self, pus, pdir_fid):
        resp = requests.post(
            f"{self._url_prefix}/save?pr=ucpro&fr=pc",
            json={
                "fid_list": [
                    self.fid,
                ],
                "fid_token_list": [
                    self.share_fid_token,
                ],
                "pdir_fid": self.pdir_fid,
                "pwd_id": self._share_id,
                "stoken": self._stoken,
                "to_pdir_fid": pdir_fid,
            },
            cookies={
                "__pus": pus,
            },
        )
        print(resp.json())
        resp.raise_for_status()

    # 批量保存方法
    def savelist(self, pus, pdir_fid, files):
        fid_list = [file.fid for file in files]
        share_fid_token_list = [file.share_fid_token for file in files]

        resp = requests.post(
            f"{self._url_prefix}/save?pr=ucpro&fr=pc",
            json={
                "fid_list": fid_list,
                "fid_token_list": share_fid_token_list,
                "pdir_fid": self.pdir_fid,
                "pwd_id": self._share_id,
                "stoken": self._stoken,
                "to_pdir_fid": pdir_fid,
            },
            cookies={
                "__pus": pus,
            },
        )
        print(resp.json())
        resp.raise_for_status()


class BaseShare:
    def __init__(self, url_prefix, share_id, code=""):
        stoken = requests.post(
            f"{url_prefix}/token",
            json={
                "pwd_id": share_id,
                "passcode": code,
            },
        ).json()["data"]["stoken"]
        auth = {
            "share_id": share_id,
            "code": code,
            "stoken": stoken,
            "url_prefix": url_prefix,
        }
        files = requests.get(
            f"{url_prefix}/detail",
            params={
                "pwd_id": share_id,
                "passcode": code,
                "stoken": stoken,
                "pdir_fid": "0",
                "_page": 1,
                "_size": 1,
            },
        ).json()["data"]["list"]
        if files:
            self.root = File(
                auth, {"file_name": "root", "fid": files[0]["pdir_fid"], "dir": True}
            )
        else:
            self.root = File(auth, {"file_name": "root", "fid": "0", "dir": True})


class UCShare(BaseShare):
    def __init__(self, share_id, code=""):
        super().__init__(
            "https://pc-api.uc.cn/1/clouddrive/share/sharepage", share_id, code
        )


class QuarkShare(BaseShare):
    def __init__(self, share_id, code=""):
        # super().__init__('https://drive-h.quark.cn/1/clouddrive/share/sharepage', share_id, code)
        super().__init__(
            "https://drive-pc.quark.cn/1/clouddrive/share/sharepage", share_id, code
        )


if __name__ == "__main__":
    quark_ck = "<夸克网盘 cookie中的__pus>"
    quark_dir = "<转存的父文件夹id(自己网盘的文件夹id，会转存到这个目录)>"
    QuarkShare("6b81947519d0").root.list()
    # 保存
    quark = QuarkShare("6b81947519d0")
    quark.root.list()[0].savelist(quark_ck, quark_dir, quark.root.list())

    # QuarkShare("6b81947519d0").root.list()[91].save(quark_ck, quark_dir)
    # uc_ck = '<uc网盘 cookie中的__pus>'
    # uc_dir = '<转存的父文件夹id>'
    # UCShare('b3528b64ec2c4').root.list()[0].save(uc_ck, uc_dir)
    # UCShare('63f31291b0f04').root.list()[0]
