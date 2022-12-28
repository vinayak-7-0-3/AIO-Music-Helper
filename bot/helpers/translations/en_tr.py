class EN(object):
    

#----------------
#
# BASICS
#
#----------------
    WELCOME_MSG  =  "Merhaba {} Efendim"
    START_DOWNLOAD  =  "İndirmeye başlanıyor........."
    ANTI_SPAM_WAIT  =  "Geçerli görevin tamamlanmasını bekleyin!"
    TASK_COMPLETED  =  "İndirme Tamamlandı"



#----------------
#
# AUTHENTICATIONS
#
#----------------
    CHAT_AUTH_SUCCESS  =  "{0} <code>{1}</code> başarıyla yetkilendirildi"
    ADD_ADMIN_SUCCESS  =  "{} yönetici olarak başarıyla eklendi"
    NO_ID_TO_AUTH  =  "Eklenecek kimlik belirtilmedi!"
    # TIDAL
    TIDAL_NOT_AUTH  = "Tidal Girişi Verilmedi."
    TIDAL_AUTH_NEXT_STEP  =  "Tidal doğrulamasını tamamlamak için sonraki {1} içinde {0}'a gidin."
    TIDAL_AUTH_SUCCESS  =  "Tidal kimlik doğrulaması başarılı. \n \n Artık {} için geçerli"
    TIDAL_ALREADY_AUTH  =  "Doğrulamanız zaten yapıldı. \n {} için geçerlidir"
    # KKBOX
    KKBOX_NOT_AUTH  =  "KKBOX hesabı kimlik bilgileri verilmedi veya abonelik süresi doldu"



#----------------
#
# MUSIC DETAILS - TELEGRAM
#
#----------------
    USER_MENTION_ALBUM  =  "❤️ <b>Isteyen :</b> {}"
    USER_MENTION_TRACK  =  "{} tarafından talep edildi"

    # TIDAL
    TIDAL_ALBUM_DETAILS = """
💽 <b>Başlık :</b> {0}
👤 <b>Sanatçı :</b> {1}
📅 <b>Yayın Tarihi :</b> {2}
📀 <b>Parça Sayısı :</b> {3}
🕒 <b>Süre :</b> {4}
🔢 <b>Cilt Sayısı :</b> {5}
"""
    # KKBOX
    KKBOX_ALBUM_DETAILS = """
🎶 <b>Başlık :</b> {0}
👤 <b>Sanatçı :</b> {1}
📅 <b>Yayın Tarihi :</b> {2}
📀 <b>Parça Sayısı :</b> {3}
"""

    # QOBUZ
    QOBUZ_ALBUM_DETAILS = """
🎶 <b>Başlık :</b> {0}
👤 <b>Sanatçı :</b> {1}
📅 <b>Yayın Tarihi :</b> {2}
📀 <b>Parça Sayısı :</b> {3}
"""

    QOBUZ_ALBUM_QUALITY_ADDON  =  "💫 <b>Kalite :</b> {}k \n "

    

    

#----------------
#
# SETTINGS PANEL
#
#----------------
    INIT_SETTINGS_MENU  =  "<b>Bot Ayarları Menüsüne Hoş Geldiniz.</b> \n \n Ayarlarını açmak için seçeneği seçin."
    WARN_REMOVE_AUTH  =  "<b>{} kimlik doğrulamasını kaldırmak istediğinizden emin misiniz?</b>"
    RM_AUTH_SUCCESSFULL  =  "{} kimlik doğrulama ayrıntısı başarıyla kaldırıldı."
    QUALITY_SET_PANEL  =  "<b>{0} \n \n Geçerli Kalite için gerekli kaliteyi seçin :</b> <code>{1}</code>"
    COMMON_AUTH_PANEL  =  "<b>{0} Kimlik Doğrulamasını Yapılandır \n \n Kimlik Doğrulama Durumu : </b>{1}"
    #
    # TIDAL PANEL
    #
    TIDAL_SETTINGS_PANEL = """
<b>Tidal Ayarlarını Burada Yapılandırın</b>
<b><u>MEVCUT AYARLAR</u></b>
<b>Kalite : </b><code>{0}</code>
<b>API : </b><code>{1}</code>
<b>Doğrulama Durumu : </b><code>{2}</code>
"""
    TIDAL_SELECT_API_KEY = """
<b><u>API ANAHTARI AYAR PANELİ</u></b>
Mevcut API Platformu : <code>{0}</code>
Kullanılabilir Biçimler : <code>{1}</code>
Geçerli API Anahtarı : <code>{2}</code>
<b><u>API PLATFORMU BİLGİSİ</u></b>
{3}
<b>API PLATFORMUNU DEĞİŞTİRDİKTEN SONRA YENİDEN OTURUM AÇMAK GEREKİR</b>
"""
    #
    # KKBOXPANEL
    #
    KKBOX_SETTINGS_PANEL = """
<b>Kkbox Ayarlarını Burada Yapılandırın</b>
<b><u>MEVCUT AYARLAR</u></b>
<b>Kalite : </b><code>{0}</code>
<b>Doğrulama Durumu : </b><code>{1}</code>
"""

    



#----------------
#
# BUTTONS
#
#----------------
    # MAIN MENU
    MAIN_MENU_BUTTON  =  "ANA MENÜ"
    TG_AUTH_BUTTON  =  "TELEGRAM AYARLARI"
    TIDAL_BUTTON  =  "GELGİT AYARLARI"
    QOBUZ_BUTTON  =  "QOBUZ AYARLARI"
    DEEZER_BUTTON  =  "DEEZER AYARLARI"
    KKBOX_BUTTON  =  'KKBOX AYARLARI'
    SOUNDCLOUD_BUTTON  =  "SOUNDCLOUD AYARLARI"
    CLOSE_BUTTON  =  "KAPAT"
    API_BUTTON  =  "API"
    # ORTAK BUTONLAR
    QUALITY_BUTTON  =  "KALİTE"
    AUTH_BUTTON  =  "YETKİLENDİR"
    REMOVE_AUTH_BUTTON  =  "YETKİ KALDIR"
    ADD_AUTH_BUTTON  =  "YETKİ EKLE"
    YES_BUTTON  =  "EVET"
    NO_BUTTON  =  "HAYIR"
    # GELİR KALİTESİ
    MASTER_QUALITY  =  "Master - FLAC"
    HIFI_QUALITY  =  "HiFi"
    HIGH_QUALITY  =  "Yüksek"
    NORMAL_QUALITY  =  "Normal"



#----------------
#
# ERRORS
#
#----------------
    # QOBUZ
    ERR_QOBUZ_NOT_STREAMABLE  =  "Bu albüm indirilemez."
