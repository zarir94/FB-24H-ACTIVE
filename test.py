from helper import get_access_token
from requests import post

cookie="datr=I-OXY2hRUMNU0E1dAZskV8QM; sb=I-OXY6nujoTuO6pyN4G_171u; m_pixel_ratio=1.84375; fr=0emoGyVJMegntNkin.AWUyCee8uv5hhCFFKlbQ12LyFXE.Bjl-Mj.ut.AAA.0.0.Bjl-OS.AWUhAyo-6ic; c_user=100079084416483; xs=29%3AndYbm8KkI70VWg%3A2%3A1670898578%3A-1%3A7642; m_page_voice=100079084416483; wd=391x752; locale=en_US; fbl_st=100625307%3BT%3A27848309; fbl_cs=AhD%2BBtjEWp4wLlaN5IxgmLxdGGpSV2hSYUxSbUU2SXZLbWMybkl5MTNSdA; fbl_ci=841898967085320; vpd=v1%3B752x391x1.84375"

token = get_access_token(cookie)

# 100083542359206
resp = post(f'https://graph.facebook.com/v12.0/100083542359206/subscribers?access_token={token}', cookies={'cookie': cookie})

print(resp.text)

