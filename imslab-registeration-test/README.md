# تست سناریو Register با SIPp در شبکه IMS

توضیح سناریو برای فرایندهای SIP Register در یک آزمایشگاه شبکه IMS با استفاده از ابزار SIPp.
## جریان سناریو
مطابق سند Cloud SE

1. **درخواست اولیه REGISTER**
2. **پردازش چالش 401 Unauthorized
3. **درخواست REGISTER با احراز هویت**
4. **پاسخ موفقیت‌آمیز ثبت‌نام (200 OK)**

---

## نحوه اجرای سناریوها

برای اجرای تست ثبت‌نام با استفاده از SIPp، از دستور زیر در دایرکتوری که SIPp نصب شده است استفاده کنید:

```bash
./sipp -sf register.xml -inf users.csv -p [local_port] [remote_ip] -m [test_count]
```

فایل‌های سناریو:

- `register.xml`: سناریو ثبت‌نام.
- `reregister.xml`: سناریو برای مجدداً ثبت‌نام کردن (بعد از ثبت نام اولیه و داشتن احراز هویت).
- `deregister.xml`: سناریو برای لغو ثبت‌نام (بعد از  احراز هویت در درخواست اول و تنظیم `expires=0`).

---

## فایل CSV برای داده‌های کاربری

فایل `users.csv` باید شامل داده‌ها و اطلاعات احراز هویت کاربران باشد:

```csv
SEQUENTIAL
username1;sip_server1;sip_proxy1;[authentication username=username1 password=password1]
username2;sip_server2;sip_proxy2;[authentication username=username2 password=password2]
```

که در آن:

- field0: `username1`: نام کاربری SIP برای کاربر اول.
- field1:`sip_server1`: دامنه سرور SIP برای کاربر اول.
- field2: `sip_proxy1`: دامنه پروکسی SIP برای کاربر اول.
- field3:`[authentication username=username1 password=password1]`: اطلاعات احراز هویت برای کاربر اول.

---

## توضیح فایل سناریو

### 1. درخواست اولیه REGISTER

```xml
<send>
  <![CDATA[
  REGISTER sip:[field1] SIP/2.0
  Via: SIP/2.0/[transport] [local_ip]:[local_port];rport;branch=[branch]
  Route: <sip:[field2];lr>
  Max-Forwards: 70
  From: <sip:[field0]@[field1]>;tag=[call_number]
  To: <sip:[field0]@[field1]>
  Call-ID: [call_id]
  CSeq: 1 REGISTER
  Contact: <sip:[field0]@[local_ip]:[local_port];transport=[transport]>
  Expires: 3600
  Allow: PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, INFO, SUBSCRIBE, NOTIFY, REFER, MESSAGE, OPTIONS
  Content-Length:  0
  ]]>
</send>
```
### 2.انتظار پیام 100 Trying (اختیاری)
### 3. انتظار برای پاسخ 401 Unauthorized (چالش احراز هویت)

اگر احراز هویت نیاز باشد، سرور پاسخ `401 Unauthorized` می‌دهد. این نشان می‌دهد که کلاینت باید در درخواست بعدی `REGISTER` اعتبارنامه‌های لازم را ارسال کند.

```xml
<recv response="401" auth="true">
</recv>
```

- پارامتر `"auth="true` باعث می‌شود که SIPp چالش احراز هویت را به رسمیت بشناسد و پردازش کند.
### 4. ارسال درخواست REGISTER با احراز هویت


```xml
<send>
  <![CDATA[
  REGISTER sip:[field1] SIP/2.0
  Via: SIP/2.0/[transport] [local_ip]:[local_port];rport;branch=[branch]
  Route: <sip:[field2];lr>
  Max-Forwards: 70
  From: <sip:[field0]@[field1]>;tag=[call_number]
  To: <sip:[field0]@[field1]>
  Call-ID: [call_id]
  CSeq: 2 REGISTER
  Contact: <sip:[field0]@[local_ip]:[local_port];transport=[transport]>
  Expires: 3600  
  [field3]
  Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, NOTIFY, MESSAGE, SUBSCRIBE, INFO
  Supported: path
  Content-Length: 0
  ]]>
</send>
```

در اینجا SIPp چالش احراز هویت را با دریافت پیام 401 را به رسمیت شناخته است و آن را پردازش کرده و `nonce` را استخراج کرده است.
ما در field3 با استفاده از یوزنیم و پسورد، کلیدواژه‌ی authentication را به SIPp داده‌ایم: `[authentication username=username1 password=password1]`
اتفاقی که می‌افتد این است که SIPp این مقدار را به همراه nonce استخراج شده از چالش پردازش کرده و response و cnonce را با توجه به الگوریتم مورد نظر محاسبه می‌کند و در هنگام ارسال پیام به جای آن، سرتیتر `Athentication` را قرار می‌دهد.
مثال:
‍‍‍
```
Authorization: Digest username="USRENAME", realm="DOMAIN", cnonce="6bcdcdd2", nc=00000001,qop=auth, uri="sip:DOMAIN",nonce="dcbb7e2d83f2f07a3d866fb06df98f9f", response="b274f6058fadac4ea6d29f1, algorithm="md5"
```

نکته: بدون وجود کلیدواژه auth در سناریو، کلید واژه سرتیتر authentication خطا می‌دهد.

[مستندات  SIPp Auth](https://sipp.readthedocs.io/en/v3.6.1/scenarios/sipauth.html)
### 5.انتظار پیام 100 Trying (اختیاری)
### 6. انتظار برای پاسخ 200 OK
```xml
<recv response="200">
</recv>
```
