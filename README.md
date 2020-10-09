# opencv-flask-web
yüz tanıma
1.Giriş
------------------------------------------------
Bu program flask üzerinden opencv kütüphanesi kullanılarak yüz tanıma yapmak için tasarlanmıştır siteye kayıt olduktan sonra kullanıcı aramanızı yüz tanıma ile yapabilirsiniz.
------------------------------------------------

2.Configrasyonlar
-------------------------------------------------
ilk önce sql yapılandırması ben sunucu olarak mysql kullandım ve sizde mysql kullanıcaksanız 58-62 satırlarını kendi sunucunuza göre yapılandırın.
ikinci olarak sql sorguları tabla isimleri users ve tablo alt başlıkları;
1 id int privatekey auto-incrament
2 name text
3 surname text
4 username text
5 email text
6 password text
7 resim longtext
---------------------------------------------------

3 EndPointler
---------------------------------------------------

Get:/
index.html
nvbar.html
logout.html
Anasayfanın olduğu yerdir.
Üzerinde nvbar vardır ve bütün işler otomatik yapılır.
Elle müdahaleye gerek yoktur.

Post:/register
register.html
Kayıt ekranının olduğu yerdir.
wtfform ile yapılandırılmış form üzerinden işlem yapar.
Sql tablosuna kayıt edilir.
sonrasında resim yükleme alanına yönlendirir.


Post:/upload
upload.html
Burada kayıt olurken kullanıcının resim yüklemesi gereken alandır.
Yüklenen resim binary koda dönüştürülüp sunucuda depolanır resimler kaybolması halinde tekrardan indirilir.
Sonrasında login ekranına yönlendirilir.

Post:/login
login.html
Giriş yapma ekranıdır.
wtfform ile tasarlanmıştır ve kullanıcı girişini denetler.
Kullanıcı bilgileri session kontrolü ile yapılır.

Get:/profil
profil.html
Burası kullanıcı bilgilerinin olduğu paneldir.
Sql sorgusu ile kullanıcı bilgileri alınır kullanılır.

Post:/logout
Kullanıcının çıkış yapmasını sağlayan bölümdür.

Post:/resimekle
resimekle.html
Bursaı gelen resimleri kayıtlı kullanıcılar arasında yüz araması yaparak eşleşen varmı diye bakılan bölümdür.
Eşleşme olması durumunda kullanıcı id si kayıt altına alınarak sql sorgusu yapılır.

Get:/sonuc
sonuc.html
Bulunan sonuc burada gösterilir resmi göster buttonu orijinal resmi göstermek içindir.

Bunun dışında massage.html ekranlarda mesaj çıkmasını sağlar.
formhelper.html ise massage.html çalışması için lazım olan dosyadır.

not : eğer kullanım sırasında ana sayfada dowload/ klasörü oluşmaz ise elle bir tane oluşturunuz. eğitim ve veri klasorlerinin içini boşaltınız.
