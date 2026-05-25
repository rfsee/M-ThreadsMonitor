import random
from datetime import datetime, timedelta
from typing import List, Dict


authors = [
    {"name": "小美談戀愛", "handle": "love_xiaomei"},
    {"name": "感情觀察家", "handle": "relationship_watcher"},
    {"name": "男友使用手冊", "handle": "bf_manual"},
    {"name": "台北愛情故事", "handle": "taipei_love"},
    {"name": "心理師艾蜜莉", "handle": "emily_psy"},
    {"name": "戀愛廢片", "handle": "love_reels"},
    {"name": "暖男日記", "handle": "warm_boy_diary"},
    {"name": "渣男辨識協會", "handle": "jerk_detector"},
    {"name": "遠距離生存指南", "handle": "ldr_survival"},
    {"name": "曖昧讓人受委屈", "handle": "ambiguous_af"},
    {"name": "情侶日常崩潰", "handle": "couple_daily"},
    {"name": "失戀陣線聯盟", "handle": "heartbreak_crew"},
    {"name": "約會美食地圖", "handle": "date_food_map"},
    {"name": "感情諮商室", "handle": "love_counsel"},
    {"name": "大學生戀愛", "handle": "college_love"},
]

sample_posts = [
    {
        "text": "真的推薦每個情侶都去玩這個「伴侶對話卡牌」！\n\n上週和男友試了一整盒，原本以為會很尷尬，結果聊到凌晨三點。\n\n有些問題是平常根本不會聊到的深度話題，像是「你覺得我們之間的安全感來自哪裡？」「你最害怕失去我的哪個面向？」\n\n玩完之後感覺感情變更好了，大推！\n\n#伴侶溝通 #情侶遊戲 #好感度提升",
        "likes": 45200,
        "replies": 892,
        "category_hint": "工具推薦",
        "date_offset_days": 1,
    },
    {
        "text": "大家覺得男生一定要有車才能交到女朋友嗎？\n\n我目前25歲，在台北工作，平時都搭捷運或ubike，生活圈也很方便，但一直被家人說沒車交不到女友。\n\n可是我自己也是女生，我反而覺得會開車沒什麼，重點是個性合不合吧？\n\n想聽聽大家的想法！\n\n#感情問題 #交往條件",
        "likes": 38700,
        "replies": 1240,
        "category_hint": "觀點爭論",
        "date_offset_days": 2,
    },
    {
        "text": "我男友昨天做了一件讓我很感動的事😭\n\n我最近工作壓力很大，每天回家都臭臉。昨天他默默煮了我最愛的麻辣鍋，還準備了我上次隨口說想喝的啤酒。\n\n吃完飯他把我抱在懷裡說：「辛苦了，不想說也沒關係，我在這邊。」\n\n當場直接噴淚😭😭😭\n\n有人也遇過這種暖男時刻嗎？\n\n#暖男 #男友 #情侶日常",
        "likes": 52300,
        "replies": 567,
        "category_hint": "案例分享",
        "date_offset_days": 0,
    },
    {
        "text": "受不了男友每次打電動就消失\n\n已經講過好幾次了，每次說「再五分鐘」然後兩小時過去了。\n\n傳訊息不讀不回，打電話也不接，等他打完了才跑來說「寶貝我錯了」。\n\n我真的心好累，是不是所有男生都這樣？\n\n#抱怨男友 #電動廢人 #情侶吵架",
        "likes": 28900,
        "replies": 2100,
        "category_hint": "抱怨",
        "date_offset_days": 1,
    },
    {
        "text": "男友的 10 種生物分類 🧬\n\n1. 電動型：打電動時會進入異次元\n2. 吃貨型：約會永遠在想要吃什麼\n3. 木頭型：你生氣了他還問「你怎麼了」\n4. 黏人型：你去上廁所他都要跟\n5. 冷笑話型：講笑話只有自己會笑\n6. 運動型：約會行程是陪他健身\n7. 攝影型：約會十分鐘拍照兩小時\n8. 睡覺型：訊息永遠已讀\r\n\n你的是哪一種？🤣\n\n#男友品種 #情侶日常 #搞笑",
        "likes": 81400,
        "replies": 3400,
        "category_hint": "幽默梗",
        "date_offset_days": 0,
    },
    {
        "text": "發現男友手機裡有交友軟體...\n\n交往三年，已經論及婚嫁。昨天借他手機查東西，不小心看到螢幕上跳出Tinder通知。\n\n我沒有偷看，但那一幕已經在腦海揮之不去。\n\n我該直接問他嗎？還是先觀察？\n\n真的好徬徨...\n\n#出軌 #感情問題 #怎麼辦",
        "likes": 67800,
        "replies": 4500,
        "category_hint": "求助請益",
        "date_offset_days": 3,
    },
    {
        "text": "推薦情侶必看的 5 部 Netflix 影集 🎬\n\n1.《愛情白皮書》- 探討長期關係的保鮮\n2.《我們之間》- 遠距離戀愛的寫實\n3.《第一次》- 初戀的美好與苦澀\n4.《婚姻故事》- 雖然有點沈重但很真實\n5.《戀愛世代》- 經典日劇重溫\n\n每一部都適合情侶一起看，看完可以討論彼此的想法！\n\n#Netflix推薦 #情侶约会 #追劇",
        "likes": 23100,
        "replies": 456,
        "category_hint": "工具推薦",
        "date_offset_days": 4,
    },
    {
        "text": "只有我覺得情侶一定要每天聊天嗎？\n\n我朋友說他們情侶有時候一整天都不聯絡，但我覺得這樣很奇怪。\n\n我和男友就算再忙，至少睡前也會講個五分鐘電話或傳個訊息。\n\n每天聊天感情才會維持吧？還是大家覺得不用？\n\n#情侶日常 #感情觀念",
        "likes": 34500,
        "replies": 1800,
        "category_hint": "觀點爭論",
        "date_offset_days": 2,
    },
    {
        "text": "分享我跟男友從遠距離到同居的過程💕\n\n台北-高雄遠距離兩年，每個月見一次面。\n\n那段時間真的很辛苦，每次分開都像失戀一次。\n\n但也是那段時間讓我們更確定彼此就是要走下去的人。\n\n今年終於一起在台中定居了！\n\n遠距離的大家加油！撐過去就是你的！\n\n#遠距離戀愛 #同居生活 #愛情故事",
        "likes": 45600,
        "replies": 723,
        "category_hint": "案例分享",
        "date_offset_days": 5,
    },
    {
        "text": "男友的「我沒事」翻譯機 🤯\n\n他說「沒事」= 有事但不想講\n他說「隨便妳」= 其實有想法但怕吵架\n他說「妳決定就好」= 到時候出錯都妳扛\n他說「我在聽」= 剛剛在放空\n他說「我錯了」= 我不知道錯在哪但先道歉再說\n\n還有什麼要補充的？🤣\n\n#男友語錄 #情侶日常 #懂的就懂",
        "likes": 92300,
        "replies": 5600,
        "category_hint": "幽默梗",
        "date_offset_days": 0,
    },
    {
        "text": "真心建議大家不要為了交往而改變自己原本的樣子。\n\n前陣子為了迎合喜歡的對象，把自己搞得面目全非，他不喜歡的東西我全部改掉，連朋友都說我像變了一個人。\n\n最後還是不適合，分手後我才發現我把自己弄丟了。\n\n先愛自己，再愛別人。\n\n#感情語錄 #戀愛建議",
        "likes": 56700,
        "replies": 890,
        "category_hint": "觀點爭論",
        "date_offset_days": 1,
    },
    {
        "text": "吵架吵到一半男友突然開始做家事⋯⋯\n\n我：你為什麼都不懂我在意的點！\n他：（默默去洗碗）\n我：你現在是在逃避問題嗎！\n他：（開始摺衣服）\n我：⋯⋯⋯⋯\n\n然後我就氣消了😅\n這是什麼求生欲啦笑死\n\n#情侶吵架 #男友求生欲 #搞笑",
        "likes": 73400,
        "replies": 2100,
        "category_hint": "幽默梗",
        "date_offset_days": 2,
    },
    {
        "text": "有人也覺得交往久了節日就不重要了嗎？\n\n和男友在一起五年，他去年忘記七夕，今年忘記情人節，還說「我們不需要用節日來證明感情」。\n\n雖然理性上知道他說的有道理，但感性上還是會失望⋯⋯\n\n是不是我太在意儀式感了？\n\n#節日儀式感 #情侶日常 #感情問題",
        "likes": 29100,
        "replies": 1300,
        "category_hint": "抱怨",
        "date_offset_days": 3,
    },
    {
        "text": "遠距離戀愛維持的 5 個小技巧 ✨\n\n1. 每天固定時間視訊（不要只是打字）\n2. 一起看劇或玩遊戲（共享體驗）\n3. 寄實體信件或小禮物（驚喜感）\n4. 規劃下次見面的行程（期待感）\n5. 坦誠溝通不安和感受\n\n走過兩年遠距的我真心分享！\n\n#遠距離 #戀愛技巧 #經驗分享",
        "likes": 38700,
        "replies": 645,
        "category_hint": "工具推薦",
        "date_offset_days": 4,
    },
    {
        "text": "我該不該原諒男友騙我？\n\n他跟我說去加班，結果被我朋友看到在酒吧。事後他解釋是同事臨時約的，怕我生氣所以說謊。\n\n不是什麼嚴重的事，但信任感一旦有裂痕就很難修補。\n\n大家覺得這種小謊言可以原諒嗎？\n\n#感情問題 #信任 #情侶",
        "likes": 41200,
        "replies": 2800,
        "category_hint": "求助請益",
        "date_offset_days": 1,
    },
    {
        "text": "分享一下我的奇葩相親經驗😂\n\n對方一坐下來就問我月薪多少、有沒有房子、婚後要不要跟公婆住。\n\n我：我們可以先自我介紹一下嗎？\n他：那些不重要，先確認價值觀合不合。\n\n我心想我連你叫什麼名字都不知道欸大哥！\n\n#相親 #奇葩經驗 #單身萬歲",
        "likes": 34100,
        "replies": 1500,
        "category_hint": "抱怨",
        "date_offset_days": 6,
    },
    {
        "text": "大家覺得伴侶之間應該要有共同興趣嗎？\n\n我和男友的興趣完全不同，我喜歡看展覽、看電影，他喜歡打球、打電動。\n\n有人說這樣互補比較好，有人說沒有共同話題很危險。\n\n我自己是覺得各自有空間也不錯啦，大家怎麼看？\n\n#感情討論 #情侶興趣",
        "likes": 25600,
        "replies": 1100,
        "category_hint": "觀點爭論",
        "date_offset_days": 3,
    },
    {
        "text": "如何辨識渣男的 7 個特徵 🚩\n\n1. 認識第一天就說你特別\n2. 從不公開你們的關係\n3. 訊息永遠回很慢但ig在線\n4. 約會總是臨時約\n5. 說「我還沒準備好進入關係」\n6. 他的朋友你不知道\n7. 對你的稱呼永遠是「寶貝」而不是名字\n\n中三個以上請直接放生🙏\n\n#渣男 #戀愛警訊 #女生必看",
        "likes": 84500,
        "replies": 4200,
        "category_hint": "工具推薦",
        "date_offset_days": 2,
    },
    {
        "text": "我終於跟我暗戀兩年的學長告白了！！！\n\n結局：他說他也要跟我說一件事，然後他就親了我🥹\n\n我們在一起了！！！！！\n\n原來雙向暗戀是真的存在的😭😭😭\n\n大家加油！勇敢告白吧！\n\n#告白成功 #雙向暗戀 #愛情小確幸",
        "likes": 98700,
        "replies": 3200,
        "category_hint": "案例分享",
        "date_offset_days": 0,
    },
    {
        "text": "幫朋友問：發現男友跟女同事單獨吃宵夜，該生氣嗎？\n\n她男友說是同事剛好下班遇到，就一起去吃了。\n\n但女生覺得不太舒服，又怕自己太小氣。\n\n大家覺得這樣是正常的社交還是該注意？\n\n#感情問題 #情侶界線 #求助",
        "likes": 36800,
        "replies": 1900,
        "category_hint": "求助請益",
        "date_offset_days": 4,
    },
]

comment_templates = [
    "完全認同！我也是這樣想的🙋",
    "不同意耶，每對情侶狀況不一樣吧",
    "感同身受⋯⋯我家的也是這樣",
    "所以結論是什麼啦XD",
    "求卡牌連結！在哪裡買？",
    "真的！說到我心坎裡了",
    "我覺得要看情況不能一概而論",
    "笑死 太中肯了🤣",
    "這根本在說我男友😂",
    "已收藏！感謝分享❤️",
    "好羨慕喔 我也想要這樣的感情",
    "等你交往久了就知道了⋯⋯",
    "重點是溝通啦 不是誰對誰錯",
    "我男友完全相反欸XD",
    "這篇必須讓另一半看到",
    "講得好好 被療癒到了🥺",
    "但也要看雙方能不能互相理解吧",
    "我也有經歷過 最後分手了😢",
    "第一點就中了 該放生嗎QQ",
    "原po加油！你不是一個人💪",
    "好甜喔我要瞎了👓",
    "這什麼求生慾笑爛🤣",
    "認真問 這樣算正常嗎？",
    "你脾氣也太好 我早翻桌了",
    "求後續！！！！",
]


def generate_comments(count: int = 5) -> List[Dict]:
    selected = random.sample(comment_templates, min(count, len(comment_templates)))
    return [
        {
            "author": f"用戶{random.randint(1000,9999)}",
            "text": text,
            "likes": random.randint(10, 2000),
            "time_ago": f"{random.randint(1,12)}小時前",
        }
        for text in selected
    ]


def generate_sample_data(max_posts: int = 20) -> List[Dict]:
    now = datetime.now()
    posts = []

    samples = random.sample(sample_posts, min(max_posts, len(sample_posts)))

    for i, sp in enumerate(samples):
        author = authors[i % len(authors)]
        post_date = now - timedelta(days=sp["date_offset_days"],
                                    hours=random.randint(0, 23),
                                    minutes=random.randint(0, 59))

        replies_count = sp["replies"]
        top_comments = generate_comments(5)

        post = {
            "id": f"thread_{now.strftime('%Y%m%d')}_{i+1:03d}",
            "author": author["name"],
            "handle": author["handle"],
            "date": post_date.strftime("%Y-%m-%d %H:%M"),
            "timestamp": int(post_date.timestamp()),
            "text": sp["text"],
            "likes": sp["likes"],
            "replies": replies_count,
            "url": f"https://www.threads.net/@{author['handle']}/post/{random.randint(1000000000000000000, 9999999999999999999)}",
            "category_hint": sp["category_hint"],
            "top_comments": top_comments,
        }
        posts.append(post)

    posts.sort(key=lambda x: x["likes"], reverse=True)
    return posts
