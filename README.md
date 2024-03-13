看见佬友们一直都在机场链接，跟个风也先分享几个刚c好的机场链接，还是热乎的哦
<details>
<summary>点击以展开</summary>

```
https://jichang.123417.xyz/api/v1/client/subscribe?token=d822f11b21d5520e662fc18276b724b2
https://jichang.123417.xyz/api/v1/client/subscribe?token=f8800a8a5c738b80b63f2fc2596699c8
https://jichang.123417.xyz/api/v1/client/subscribe?token=a31be7d6999f41b690c830cec79be2ed

https://www.kuaidog005.top/api/v1/client/subscribe?token=6d860c2b3c9f22930e2f6d78b556a6bf
https://www.kuaidog005.top/api/v1/client/subscribe?token=ced805757db63d64cf0403588ae7fe4c
https://www.kuaidog005.top/api/v1/client/subscribe?token=344e2f47a413272a91e1f25a3fe241fa

https://www.kuaidog005.top/api/v1/client/subscribe?token=6ae2933c78c19b516cc835cc469ff06e
https://jichang.123417.xyz/api/v1/client/subscribe?token=ab9d95bb150232587ebd0e4e438c667e
https://m11.spwvpn.com/api/v1/client/subscribe?token=70bef7df732986935dffccd1ef2579d3
```

</details>

写了一个专门可以自动获取v2board系列的机场链接的demo项目地址如下：
https://github.com/snailyp/airport-link

==在介绍项目之前，先简单介绍一下v2board机场。

### v2board机场
目前大多数的机场都是采用的[v2board](https://github.com/v2board/v2board)开源项目，搭建的机场网站，除了UI页面不同之外，其实底层调用的api可以说是完全一样。总结了主要有以下接口：
```
# 注册uri
REGISTER_SUFFIX_URI = "/api/v1/passport/auth/register"
# 登录uri
LOGIN_SUFFIX_URI = "/api/v1/passport/auth/login"
# 发送邮箱uri
SEND_EMAIL_SUFFIX_URI = "/api/v1/passport/comm/sendEmailVerify"
# 获取套餐uri
PLAN_FETCH_SUFFIX_URI = "/api/v1/user/plan/fetch"
# 校验优惠码uri
CHECK_COUPON_SUFFIX_URI = "/api/v1/user/coupon/check"
# 获取支付方式uri
PAYMENT_METHOD_URI = "/api/v1/user/order/getPaymentMethod"
# 下单uri
ORDER_SUFFIX_URI = "/api/v1/user/order/save"
# 结账uri
CHECK_OUT_SUFFIX_URI = "/api/v1/user/order/checkout"
# 获取订阅地址uri
GET_SUBSCRIBE_URI = "/api/v1/user/getSubscribe"
```
所以检验一个机场是否是v2board机场，只要调用其中的一个接口，测试就可以判断出来。例如：
调用/api/v1/user/plan/fetch套餐接口，它会返回这个消息：

```json
{
    "message": "\u672a\u767b\u5f55\u6216\u767b\u9646\u5df2\u8fc7\u671f"
}
```
这就证明了这个机场是v2board机场。那么就可以用我的项目进行C了，接下来简单介绍一下项目
### 项目介绍
#### 1. 功能

1.1 支持半自动化生成outlook邮箱(也可用于c copilot)
  * 图形验证部分需要手工，其余自动

1.2 支持v2board系列机场注册获取机场链接
  * 支持无邮箱验证和有邮箱验证
  * 支持有优惠码和无优惠码
  * 支持机场链接和账号保存
#### 2. 配置

#### 2.1 配置websites.txt
格式如下：
机场地址,是否有邮箱验证(t表示有，f表示没有),优惠码（有则填没有就空着），每行一个机场数据。示例如下：

```
https://www.kuaidog005.top,f,baipiao
https://jichang.123417.xyz,t,
https://m2.spwvpn.com,t,
```
#### 2.2 (可选)配置outlook_accounts.txt
格式如下：
邮箱:密码 （每行一个邮箱账号）
示例如下：
```
FZ7mhFEbQJU@outlook.com:CtZNf&53V7jyp3IQD%OG
FxDMRpQJ6ak@outlook.com:3J4uiDUXKcahMFW8BLmr
```
**注意**：`目前项目仅支持outlook邮箱，没有outlook邮箱也没关系，先不填，项目包含了自动生成outlook邮箱，并保存在该文件下，后面介绍具体怎么生成`。

#### 2.3 配置config.json
**如果需要生成outlook邮箱，需要修改该配置。**
需要修改以下两个配置：
* executablePath为chrome浏览器的可执行文件地址
* proxy为代理地址，代理选ip干净一点的，不然后面图形验证会比较麻烦

**如果需要机场地址需要代理访问，也需要配置proxy**
```
"executablePath": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
"proxy": "http://127.0.0.1:7892",
```
### 3. 项目运行

#### 3.1 安装依赖
首先，你需要确保你已经安装了`pip`。你可以通过在命令行中输入以下命令来检查：

```
pip --version
```

如果你看到了版本信息，那就表明你已经安装了`pip`。如果没有，你需要首先安装`pip`。
```bash
pip install -r requirements.txt
``` 
#### 3.2 生成outlook邮箱
首先，cd到项目根目录，然后执行命令
```
python .\outlook_account.py
```
执行命令后，会自动的弹出浏览器，然后自动填充必要信息，到了图形验证的时候，需要手动的通过一下验证，接着会跳出下面这个页面，需手动点击一下确定，就生成好了一个outlook邮箱，生成好的邮箱会保存在outlook_accounts.txt中
![Snipaste_2024-03-11_22-22-21.png](pic%2FSnipaste_2024-03-11_22-22-21.png)

#### 3.3 生成机场链接
首先，cd到项目根目录，然后执行命令
```
python .\main.py
```
执行命令后，会在控制台打印必要信息以及输出链接信息。执行结束会生成airport_link_info.txt文件，里面包含了机场的账号信息以及对应机场链接

### 4. 免费白嫖机场
#### 4.1 近期有活动的机场
```
https://www.kuaidog005.top
https://jichang.123417.xyz
https://m2.spwvpn.com
```
#### 4.2 个人关注的一些白嫖机场频道
会定期分享白嫖机场
https://t.me/bpyl666
https://t.me/wxgqlfx
https://t.me/sxtnbhz

好了，就介绍这么多吧，对你有帮助的话，希望佬友们点点赞 :face_with_peeking_eye: :face_with_peeking_eye: :face_with_peeking_eye:

