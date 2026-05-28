# gen_vocab_ext.py — generate kanji-map-vocab-ext.js
# Comprehensive vocab for N5/N4/N3 kanji in kanji-map

vocab_data = [
# === 下 ===
  {'id':'地下','reading':'ちか','meaning':'tầng hầm, dưới lòng đất','kanji':['下'],'jlpt':'N4','pitch':0,'example_jp':'地下に駐車場があります。','example_vi':'Có bãi đỗ xe ở tầng hầm.'},
  {'id':'下手','reading':'へた','meaning':'kém cỏi, vụng về','kanji':['下','手'],'jlpt':'N5','pitch':2,'example_jp':'私は料理が下手です。','example_vi':'Tôi nấu ăn kém.'},
  {'id':'靴下','reading':'くつした','meaning':'tất, bít tất','kanji':['下'],'jlpt':'N5','pitch':3,'example_jp':'靴下を履いてください。','example_vi':'Hãy đi tất vào.'},
  {'id':'地下鉄','reading':'ちかてつ','meaning':'tàu điện ngầm','kanji':['下'],'jlpt':'N5','pitch':3,'example_jp':'地下鉄で行きます。','example_vi':'Tôi đi bằng tàu điện ngầm.'},
  {'id':'以下','reading':'いか','meaning':'dưới, kém hơn, từ đây trở xuống','kanji':['下'],'jlpt':'N4','pitch':1,'example_jp':'18歳以下は入れません。','example_vi':'Dưới 18 tuổi không được vào.'},
  {'id':'下がる','reading':'さがる','meaning':'giảm xuống, đi xuống','kanji':['下'],'jlpt':'N4','pitch':0,'example_jp':'気温が下がりました。','example_vi':'Nhiệt độ đã giảm.'},
  {'id':'下げる','reading':'さげる','meaning':'hạ xuống, giảm','kanji':['下'],'jlpt':'N4','pitch':0,'example_jp':'値段を下げる。','example_vi':'Hạ giá xuống.'},
  {'id':'下る','reading':'くだる','meaning':'đi xuống, hạ lưu','kanji':['下'],'jlpt':'N4','pitch':2,'example_jp':'坂を下る。','example_vi':'Đi xuống dốc.'},
  {'id':'下りる','reading':'おりる','meaning':'xuống (xe, cầu thang...)','kanji':['下'],'jlpt':'N4','pitch':0,'example_jp':'バスを下りた。','example_vi':'Xuống xe buýt.'},
  {'id':'下着','reading':'したぎ','meaning':'đồ lót, quần áo mặc trong','kanji':['下'],'jlpt':'N4','pitch':0,'example_jp':'下着を洗濯する。','example_vi':'Giặt đồ lót.'},
# === 上 ===
  {'id':'上手','reading':'じょうず','meaning':'khéo léo, giỏi','kanji':['上','手'],'jlpt':'N5','pitch':0,'example_jp':'彼は料理が上手です。','example_vi':'Anh ấy nấu ăn giỏi.'},
  {'id':'上がる','reading':'あがる','meaning':'lên, tăng','kanji':['上'],'jlpt':'N4','pitch':0,'example_jp':'気温が上がった。','example_vi':'Nhiệt độ tăng lên.'},
  {'id':'上げる','reading':'あげる','meaning':'nâng lên, tăng','kanji':['上'],'jlpt':'N4','pitch':0,'example_jp':'手を上げてください。','example_vi':'Hãy giơ tay lên.'},
  {'id':'以上','reading':'いじょう','meaning':'hơn, trên, từ đây trở lên','kanji':['上'],'jlpt':'N4','pitch':1,'example_jp':'18歳以上の方。','example_vi':'Người từ 18 tuổi trở lên.'},
  {'id':'上着','reading':'うわぎ','meaning':'áo khoác ngoài','kanji':['上'],'jlpt':'N5','pitch':3,'example_jp':'上着を着てください。','example_vi':'Hãy mặc áo khoác vào.'},
  {'id':'屋上','reading':'おくじょう','meaning':'sân thượng','kanji':['上'],'jlpt':'N3','pitch':0,'example_jp':'屋上から景色が見える。','example_vi':'Nhìn thấy cảnh đẹp từ sân thượng.'},
  {'id':'上司','reading':'じょうし','meaning':'cấp trên, sếp','kanji':['上'],'jlpt':'N3','pitch':1,'example_jp':'上司に相談する。','example_vi':'Hỏi ý kiến cấp trên.'},
  {'id':'向上','reading':'こうじょう','meaning':'nâng cao, cải thiện','kanji':['上'],'jlpt':'N3','pitch':0,'example_jp':'技術を向上させる。','example_vi':'Nâng cao kỹ thuật.'},
  {'id':'上達','reading':'じょうたつ','meaning':'tiến bộ, thành thạo hơn','kanji':['上'],'jlpt':'N3','pitch':0,'example_jp':'日本語が上達した。','example_vi':'Tiếng Nhật tiến bộ hơn.'},
# === 大 ===
  {'id':'大きい','reading':'おおきい','meaning':'to lớn','kanji':['大'],'jlpt':'N5','pitch':4,'example_jp':'大きい家に住みたい。','example_vi':'Tôi muốn sống trong ngôi nhà to lớn.'},
  {'id':'大学','reading':'だいがく','meaning':'đại học','kanji':['大','学'],'jlpt':'N5','pitch':0,'example_jp':'大学で勉強しています。','example_vi':'Tôi đang học ở đại học.'},
  {'id':'大人','reading':'おとな','meaning':'người lớn, trưởng thành','kanji':['大','人'],'jlpt':'N5','pitch':0,'example_jp':'大人になりたい。','example_vi':'Tôi muốn trở thành người lớn.'},
  {'id':'大切','reading':'たいせつ','meaning':'quan trọng, quý giá','kanji':['大'],'jlpt':'N4','pitch':0,'example_jp':'家族が大切です。','example_vi':'Gia đình rất quan trọng.'},
  {'id':'大丈夫','reading':'だいじょうぶ','meaning':'ổn thôi, không sao','kanji':['大'],'jlpt':'N5','pitch':3,'example_jp':'大丈夫ですか？','example_vi':'Bạn có ổn không?'},
  {'id':'大好き','reading':'だいすき','meaning':'rất thích','kanji':['大'],'jlpt':'N5','pitch':0,'example_jp':'日本語が大好きです。','example_vi':'Tôi rất thích tiếng Nhật.'},
  {'id':'大変','reading':'たいへん','meaning':'khó khăn, vất vả; rất','kanji':['大'],'jlpt':'N4','pitch':0,'example_jp':'大変な仕事ですね。','example_vi':'Công việc vất vả nhỉ.'},
  {'id':'大会','reading':'たいかい','meaning':'đại hội, giải thi đấu','kanji':['大','会'],'jlpt':'N3','pitch':0,'example_jp':'スポーツ大会に参加する。','example_vi':'Tham gia đại hội thể thao.'},
  {'id':'拡大','reading':'かくだい','meaning':'mở rộng, khuếch đại','kanji':['大'],'jlpt':'N3','pitch':0,'example_jp':'事業を拡大する。','example_vi':'Mở rộng kinh doanh.'},
  {'id':'大雨','reading':'おおあめ','meaning':'mưa to, mưa lớn','kanji':['大','雨'],'jlpt':'N4','pitch':2,'example_jp':'大雨が降っている。','example_vi':'Đang mưa to.'},
# === 小 ===
  {'id':'小さい','reading':'ちいさい','meaning':'nhỏ bé','kanji':['小'],'jlpt':'N5','pitch':4,'example_jp':'小さい子供がいる。','example_vi':'Có đứa trẻ nhỏ.'},
  {'id':'小学校','reading':'しょうがっこう','meaning':'trường tiểu học','kanji':['小','学'],'jlpt':'N5','pitch':5,'example_jp':'小学校に通っています。','example_vi':'Tôi đang học trường tiểu học.'},
  {'id':'小説','reading':'しょうせつ','meaning':'tiểu thuyết','kanji':['小'],'jlpt':'N4','pitch':0,'example_jp':'小説を読むのが好きです。','example_vi':'Tôi thích đọc tiểu thuyết.'},
  {'id':'小鳥','reading':'ことり','meaning':'chim nhỏ','kanji':['小'],'jlpt':'N4','pitch':0,'example_jp':'小鳥が歌っている。','example_vi':'Chú chim nhỏ đang hót.'},
  {'id':'最小','reading':'さいしょう','meaning':'tối thiểu, nhỏ nhất','kanji':['小'],'jlpt':'N3','pitch':0,'example_jp':'最小限のコストで作る。','example_vi':'Sản xuất với chi phí tối thiểu.'},
  {'id':'小川','reading':'おがわ','meaning':'suối nhỏ, dòng khe','kanji':['小','川'],'jlpt':'N4','pitch':0,'example_jp':'小川のそばで休む。','example_vi':'Nghỉ ngơi bên bờ suối nhỏ.'},
# === 中 ===
  {'id':'中学校','reading':'ちゅうがっこう','meaning':'trường trung học cơ sở','kanji':['中','学'],'jlpt':'N5','pitch':5,'example_jp':'中学校で英語を習いました。','example_vi':'Tôi học tiếng Anh ở THCS.'},
  {'id':'中心','reading':'ちゅうしん','meaning':'trung tâm, cốt lõi','kanji':['中'],'jlpt':'N3','pitch':0,'example_jp':'町の中心にあります。','example_vi':'Nằm ở trung tâm thị trấn.'},
  {'id':'中国','reading':'ちゅうごく','meaning':'Trung Quốc','kanji':['中'],'jlpt':'N5','pitch':0,'example_jp':'中国語を勉強しています。','example_vi':'Tôi đang học tiếng Trung.'},
  {'id':'世界中','reading':'せかいじゅう','meaning':'khắp thế giới','kanji':['中'],'jlpt':'N4','pitch':4,'example_jp':'世界中を旅したい。','example_vi':'Tôi muốn du lịch khắp thế giới.'},
  {'id':'途中','reading':'とちゅう','meaning':'giữa chừng, trên đường','kanji':['中'],'jlpt':'N3','pitch':0,'example_jp':'途中で雨が降ってきた。','example_vi':'Đi giữa chừng thì trời đổ mưa.'},
  {'id':'集中','reading':'しゅうちゅう','meaning':'tập trung','kanji':['中'],'jlpt':'N3','pitch':0,'example_jp':'勉強に集中する。','example_vi':'Tập trung vào việc học.'},
  {'id':'中身','reading':'なかみ','meaning':'nội dung, bên trong','kanji':['中'],'jlpt':'N3','pitch':0,'example_jp':'箱の中身を確認する。','example_vi':'Kiểm tra nội dung hộp.'},
# === 人 ===
  {'id':'外国人','reading':'がいこくじん','meaning':'người nước ngoài','kanji':['人'],'jlpt':'N5','pitch':5,'example_jp':'外国人の友達がいる。','example_vi':'Tôi có bạn người nước ngoài.'},
  {'id':'個人','reading':'こじん','meaning':'cá nhân','kanji':['人'],'jlpt':'N3','pitch':1,'example_jp':'個人情報を守る。','example_vi':'Bảo vệ thông tin cá nhân.'},
  {'id':'人口','reading':'じんこう','meaning':'dân số','kanji':['人','口'],'jlpt':'N4','pitch':0,'example_jp':'日本の人口は約1億人です。','example_vi':'Dân số Nhật Bản khoảng 100 triệu người.'},
  {'id':'人気','reading':'にんき','meaning':'nổi tiếng, được yêu thích','kanji':['人'],'jlpt':'N4','pitch':1,'example_jp':'この映画は人気があります。','example_vi':'Bộ phim này rất nổi tiếng.'},
  {'id':'社会人','reading':'しゃかいじん','meaning':'người đi làm','kanji':['人'],'jlpt':'N3','pitch':5,'example_jp':'来年から社会人になります。','example_vi':'Từ năm sau tôi sẽ đi làm.'},
  {'id':'人間','reading':'にんげん','meaning':'con người, nhân loại','kanji':['人','間'],'jlpt':'N4','pitch':0,'example_jp':'人間は考える生き物だ。','example_vi':'Con người là sinh vật biết suy nghĩ.'},
  {'id':'人生','reading':'じんせい','meaning':'cuộc đời','kanji':['人','生'],'jlpt':'N3','pitch':1,'example_jp':'人生は短い。','example_vi':'Cuộc đời ngắn ngủi.'},
# === 山 ===
  {'id':'富士山','reading':'ふじさん','meaning':'núi Fuji','kanji':['山'],'jlpt':'N5','pitch':3,'example_jp':'富士山に登りたい。','example_vi':'Tôi muốn leo núi Fuji.'},
  {'id':'火山','reading':'かざん','meaning':'núi lửa','kanji':['山','火'],'jlpt':'N4','pitch':0,'example_jp':'活火山が噴火した。','example_vi':'Núi lửa đang hoạt động đã phun.'},
  {'id':'山登り','reading':'やまのぼり','meaning':'leo núi','kanji':['山'],'jlpt':'N4','pitch':4,'example_jp':'山登りが趣味です。','example_vi':'Leo núi là sở thích của tôi.'},
  {'id':'山道','reading':'やまみち','meaning':'đường núi','kanji':['山','道'],'jlpt':'N4','pitch':0,'example_jp':'山道を歩く。','example_vi':'Đi bộ trên đường núi.'},
# === 国 ===
  {'id':'外国','reading':'がいこく','meaning':'nước ngoài','kanji':['国'],'jlpt':'N5','pitch':0,'example_jp':'外国に行きたい。','example_vi':'Tôi muốn đi nước ngoài.'},
  {'id':'国際','reading':'こくさい','meaning':'quốc tế','kanji':['国'],'jlpt':'N3','pitch':0,'example_jp':'国際会議に参加する。','example_vi':'Tham gia hội nghị quốc tế.'},
  {'id':'国語','reading':'こくご','meaning':'quốc ngữ, tiếng mẹ đẻ','kanji':['国'],'jlpt':'N4','pitch':1,'example_jp':'国語の宿題をする。','example_vi':'Làm bài tập quốc ngữ.'},
  {'id':'国民','reading':'こくみん','meaning':'nhân dân, công dân','kanji':['国'],'jlpt':'N3','pitch':2,'example_jp':'国民の声を聞く。','example_vi':'Lắng nghe tiếng nói nhân dân.'},
  {'id':'帰国','reading':'きこく','meaning':'về nước, hồi hương','kanji':['国'],'jlpt':'N3','pitch':0,'example_jp':'来月帰国します。','example_vi':'Tháng sau tôi về nước.'},
  {'id':'島国','reading':'しまぐに','meaning':'đảo quốc, quốc gia đảo','kanji':['国'],'jlpt':'N4','pitch':3,'example_jp':'日本は島国です。','example_vi':'Nhật Bản là đảo quốc.'},
# === 年 ===
  {'id':'去年','reading':'きょねん','meaning':'năm ngoái','kanji':['年'],'jlpt':'N5','pitch':2,'example_jp':'去年日本に行きました。','example_vi':'Năm ngoái tôi đã đi Nhật.'},
  {'id':'今年','reading':'ことし','meaning':'năm nay','kanji':['年'],'jlpt':'N5','pitch':2,'example_jp':'今年の目標は何ですか？','example_vi':'Mục tiêu năm nay của bạn là gì?'},
  {'id':'来年','reading':'らいねん','meaning':'năm sau','kanji':['年'],'jlpt':'N5','pitch':0,'example_jp':'来年また会いましょう。','example_vi':'Năm sau gặp lại nhé.'},
  {'id':'少年','reading':'しょうねん','meaning':'thiếu niên','kanji':['年'],'jlpt':'N4','pitch':1,'example_jp':'少年の頃の夢がある。','example_vi':'Có giấc mơ từ thời thiếu niên.'},
  {'id':'青年','reading':'せいねん','meaning':'thanh niên','kanji':['年'],'jlpt':'N3','pitch':1,'example_jp':'青年たちが集まる。','example_vi':'Thanh niên tụ tập lại.'},
  {'id':'年齢','reading':'ねんれい','meaning':'tuổi tác, độ tuổi','kanji':['年'],'jlpt':'N3','pitch':0,'example_jp':'年齢を教えてください。','example_vi':'Cho tôi biết tuổi của bạn.'},
  {'id':'中年','reading':'ちゅうねん','meaning':'trung niên','kanji':['年','中'],'jlpt':'N3','pitch':0,'example_jp':'中年になると体重が増える。','example_vi':'Đến tuổi trung niên thì dễ tăng cân.'},
  {'id':'年間','reading':'ねんかん','meaning':'hàng năm, trong một năm','kanji':['年'],'jlpt':'N4','pitch':1,'example_jp':'年間を通じて営業しています。','example_vi':'Kinh doanh quanh năm.'},
# === 月 ===
  {'id':'月曜日','reading':'げつようび','meaning':'thứ hai','kanji':['月'],'jlpt':'N5','pitch':5,'example_jp':'月曜日に学校があります。','example_vi':'Thứ hai tôi có trường.'},
  {'id':'来月','reading':'らいげつ','meaning':'tháng sau','kanji':['月'],'jlpt':'N5','pitch':1,'example_jp':'来月旅行に行きます。','example_vi':'Tháng sau tôi đi du lịch.'},
  {'id':'先月','reading':'せんげつ','meaning':'tháng trước','kanji':['月'],'jlpt':'N5','pitch':1,'example_jp':'先月は忙しかった。','example_vi':'Tháng trước tôi rất bận.'},
  {'id':'毎月','reading':'まいつき','meaning':'hàng tháng, mỗi tháng','kanji':['月'],'jlpt':'N5','pitch':0,'example_jp':'毎月貯金しています。','example_vi':'Tôi tiết kiệm hàng tháng.'},
  {'id':'月見','reading':'つきみ','meaning':'ngắm trăng','kanji':['月'],'jlpt':'N4','pitch':0,'example_jp':'秋に月見をします。','example_vi':'Mùa thu ngắm trăng.'},
  {'id':'満月','reading':'まんげつ','meaning':'trăng tròn','kanji':['月'],'jlpt':'N4','pitch':0,'example_jp':'今夜は満月だ。','example_vi':'Tối nay trăng tròn.'},
# === 日 ===
  {'id':'今日','reading':'きょう','meaning':'hôm nay','kanji':['日'],'jlpt':'N5','pitch':1,'example_jp':'今日は何曜日ですか？','example_vi':'Hôm nay là thứ mấy?'},
  {'id':'昨日','reading':'きのう','meaning':'hôm qua','kanji':['日'],'jlpt':'N5','pitch':2,'example_jp':'昨日映画を見ました。','example_vi':'Hôm qua tôi đã xem phim.'},
  {'id':'明日','reading':'あした','meaning':'ngày mai','kanji':['日'],'jlpt':'N5','pitch':3,'example_jp':'明日また来てください。','example_vi':'Ngày mai hãy đến lại nhé.'},
  {'id':'日記','reading':'にっき','meaning':'nhật ký','kanji':['日'],'jlpt':'N4','pitch':0,'example_jp':'毎日日記を書いています。','example_vi':'Tôi viết nhật ký mỗi ngày.'},
  {'id':'休日','reading':'きゅうじつ','meaning':'ngày nghỉ','kanji':['日'],'jlpt':'N4','pitch':0,'example_jp':'休日は家族と過ごす。','example_vi':'Ngày nghỉ tôi ở bên gia đình.'},
  {'id':'祝日','reading':'しゅくじつ','meaning':'ngày lễ quốc gia','kanji':['日'],'jlpt':'N4','pitch':0,'example_jp':'明日は祝日です。','example_vi':'Ngày mai là ngày lễ.'},
  {'id':'日常','reading':'にちじょう','meaning':'hằng ngày, thường ngày','kanji':['日'],'jlpt':'N3','pitch':0,'example_jp':'日常生活を楽しむ。','example_vi':'Tận hưởng cuộc sống hằng ngày.'},
  {'id':'日程','reading':'にってい','meaning':'lịch trình, chương trình','kanji':['日'],'jlpt':'N3','pitch':0,'example_jp':'日程を確認する。','example_vi':'Xác nhận lịch trình.'},
# === 時 ===
  {'id':'時計','reading':'とけい','meaning':'đồng hồ','kanji':['時'],'jlpt':'N5','pitch':0,'example_jp':'時計を見てください。','example_vi':'Hãy nhìn đồng hồ.'},
  {'id':'時代','reading':'じだい','meaning':'thời đại, thời kỳ','kanji':['時'],'jlpt':'N3','pitch':0,'example_jp':'平和な時代に生まれた。','example_vi':'Sinh ra trong thời đại hòa bình.'},
  {'id':'時間割','reading':'じかんわり','meaning':'thời khóa biểu','kanji':['時'],'jlpt':'N4','pitch':4,'example_jp':'時間割を確認する。','example_vi':'Kiểm tra thời khóa biểu.'},
  {'id':'同時','reading':'どうじ','meaning':'đồng thời, cùng lúc','kanji':['時'],'jlpt':'N3','pitch':1,'example_jp':'二つのことを同時にする。','example_vi':'Làm hai việc cùng một lúc.'},
  {'id':'当時','reading':'とうじ','meaning':'lúc đó, hồi đó','kanji':['時'],'jlpt':'N3','pitch':1,'example_jp':'当時は若かった。','example_vi':'Hồi đó tôi còn trẻ.'},
# === 間 ===
  {'id':'時間','reading':'じかん','meaning':'thời gian','kanji':['時','間'],'jlpt':'N5','pitch':0,'example_jp':'時間がありません。','example_vi':'Tôi không có thời gian.'},
  {'id':'空間','reading':'くうかん','meaning':'không gian','kanji':['間'],'jlpt':'N3','pitch':0,'example_jp':'広い空間が必要だ。','example_vi':'Cần không gian rộng.'},
  {'id':'間違い','reading':'まちがい','meaning':'lỗi, nhầm lẫn','kanji':['間'],'jlpt':'N4','pitch':4,'example_jp':'間違いを犯してしまった。','example_vi':'Tôi đã mắc lỗi.'},
  {'id':'週間','reading':'しゅうかん','meaning':'tuần (đơn vị thời gian)','kanji':['間'],'jlpt':'N5','pitch':0,'example_jp':'一週間に一度会う。','example_vi':'Gặp nhau một lần một tuần.'},
  {'id':'瞬間','reading':'しゅんかん','meaning':'khoảnh khắc','kanji':['間'],'jlpt':'N3','pitch':0,'example_jp':'その瞬間を忘れない。','example_vi':'Tôi không quên khoảnh khắc đó.'},
# === 水 ===
  {'id':'水泳','reading':'すいえい','meaning':'bơi lội','kanji':['水'],'jlpt':'N4','pitch':0,'example_jp':'水泳が得意です。','example_vi':'Tôi giỏi bơi lội.'},
  {'id':'水道','reading':'すいどう','meaning':'đường ống nước, cấp nước','kanji':['水'],'jlpt':'N4','pitch':0,'example_jp':'水道料金を払う。','example_vi':'Trả tiền nước.'},
  {'id':'洪水','reading':'こうずい','meaning':'lũ lụt','kanji':['水'],'jlpt':'N4','pitch':0,'example_jp':'大雨で洪水が起きた。','example_vi':'Mưa lớn gây lũ lụt.'},
  {'id':'水分','reading':'すいぶん','meaning':'nước (trong cơ thể), độ ẩm','kanji':['水','分'],'jlpt':'N3','pitch':1,'example_jp':'水分をしっかり取る。','example_vi':'Uống đủ nước.'},
  {'id':'水準','reading':'すいじゅん','meaning':'mức độ, tiêu chuẩn','kanji':['水'],'jlpt':'N3','pitch':0,'example_jp':'生活水準が上がった。','example_vi':'Mức sống nâng cao.'},
# === 火 ===
  {'id':'火事','reading':'かじ','meaning':'đám cháy, hỏa hoạn','kanji':['火'],'jlpt':'N4','pitch':1,'example_jp':'火事で家が燃えた。','example_vi':'Nhà bị cháy trong hỏa hoạn.'},
  {'id':'花火','reading':'はなび','meaning':'pháo hoa','kanji':['火','花'],'jlpt':'N5','pitch':1,'example_jp':'夏に花火を見ます。','example_vi':'Mùa hè tôi xem pháo hoa.'},
  {'id':'火力','reading':'かりょく','meaning':'hỏa lực, nhiệt lượng','kanji':['火'],'jlpt':'N3','pitch':1,'example_jp':'火力発電所がある。','example_vi':'Có nhà máy điện nhiệt.'},
  {'id':'火曜日','reading':'かようび','meaning':'thứ ba','kanji':['火'],'jlpt':'N5','pitch':3,'example_jp':'火曜日は授業がある。','example_vi':'Thứ ba tôi có tiết học.'},
  {'id':'点火','reading':'てんか','meaning':'châm lửa, bật lửa','kanji':['火'],'jlpt':'N4','pitch':1,'example_jp':'エンジンに点火する。','example_vi':'Bật động cơ.'},
# === 木 ===
  {'id':'木曜日','reading':'もくようび','meaning':'thứ năm','kanji':['木'],'jlpt':'N5','pitch':5,'example_jp':'木曜日に試験があります。','example_vi':'Thứ năm có kỳ thi.'},
  {'id':'木材','reading':'もくざい','meaning':'gỗ, vật liệu gỗ','kanji':['木'],'jlpt':'N3','pitch':0,'example_jp':'木材でテーブルを作る。','example_vi':'Làm bàn bằng gỗ.'},
  {'id':'植木','reading':'うえき','meaning':'cây trồng trong chậu/vườn','kanji':['木'],'jlpt':'N4','pitch':0,'example_jp':'植木に水をやる。','example_vi':'Tưới nước cho cây cảnh.'},
  {'id':'大木','reading':'たいぼく','meaning':'cây to lớn','kanji':['木','大'],'jlpt':'N4','pitch':2,'example_jp':'公園に大木がある。','example_vi':'Có cây to trong công viên.'},
# === 金 ===
  {'id':'金曜日','reading':'きんようび','meaning':'thứ sáu','kanji':['金'],'jlpt':'N5','pitch':5,'example_jp':'金曜日の夜は楽しい。','example_vi':'Tối thứ sáu rất vui.'},
  {'id':'お金','reading':'おかね','meaning':'tiền','kanji':['金'],'jlpt':'N5','pitch':0,'example_jp':'お金が足りない。','example_vi':'Không đủ tiền.'},
  {'id':'料金','reading':'りょうきん','meaning':'phí, giá tiền','kanji':['金'],'jlpt':'N4','pitch':0,'example_jp':'料金はいくらですか？','example_vi':'Phí là bao nhiêu?'},
  {'id':'金額','reading':'きんがく','meaning':'số tiền, kim ngạch','kanji':['金'],'jlpt':'N3','pitch':0,'example_jp':'金額を確認する。','example_vi':'Xác nhận số tiền.'},
  {'id':'奨学金','reading':'しょうがくきん','meaning':'học bổng','kanji':['金'],'jlpt':'N3','pitch':5,'example_jp':'奨学金をもらった。','example_vi':'Tôi nhận được học bổng.'},
  {'id':'貯金','reading':'ちょきん','meaning':'tiết kiệm tiền','kanji':['金'],'jlpt':'N4','pitch':0,'example_jp':'毎月貯金している。','example_vi':'Tôi tiết kiệm mỗi tháng.'},
# === 土 ===
  {'id':'土曜日','reading':'どようび','meaning':'thứ bảy','kanji':['土'],'jlpt':'N5','pitch':5,'example_jp':'土曜日はどこかへ行きますか？','example_vi':'Thứ bảy bạn đi đâu không?'},
  {'id':'土地','reading':'とち','meaning':'đất đai, địa điểm','kanji':['土'],'jlpt':'N4','pitch':1,'example_jp':'土地を買いたい。','example_vi':'Tôi muốn mua đất.'},
  {'id':'土台','reading':'どだい','meaning':'nền móng, cơ sở','kanji':['土'],'jlpt':'N3','pitch':0,'example_jp':'建物の土台が大切だ。','example_vi':'Nền móng của tòa nhà rất quan trọng.'},
  {'id':'粘土','reading':'ねんど','meaning':'đất sét','kanji':['土'],'jlpt':'N4','pitch':1,'example_jp':'粘土で人形を作る。','example_vi':'Nặn búp bê bằng đất sét.'},
# === 学 ===
  {'id':'学習','reading':'がくしゅう','meaning':'học tập','kanji':['学'],'jlpt':'N3','pitch':0,'example_jp':'毎日学習する習慣をつける。','example_vi':'Tạo thói quen học tập mỗi ngày.'},
  {'id':'留学','reading':'りゅうがく','meaning':'du học','kanji':['学'],'jlpt':'N3','pitch':0,'example_jp':'日本に留学したい。','example_vi':'Tôi muốn du học tại Nhật.'},
  {'id':'学部','reading':'がくぶ','meaning':'khoa (đại học)','kanji':['学'],'jlpt':'N3','pitch':1,'example_jp':'文学部に入った。','example_vi':'Tôi vào khoa văn học.'},
  {'id':'入学','reading':'にゅうがく','meaning':'nhập học, vào trường','kanji':['学'],'jlpt':'N4','pitch':0,'example_jp':'来年大学に入学する。','example_vi':'Năm sau tôi vào đại học.'},
  {'id':'卒業','reading':'そつぎょう','meaning':'tốt nghiệp','kanji':['学'],'jlpt':'N4','pitch':0,'example_jp':'来年大学を卒業します。','example_vi':'Năm sau tôi tốt nghiệp đại học.'},
  {'id':'奨学金','reading':'しょうがくきん','meaning':'học bổng','kanji':['学','金'],'jlpt':'N3','pitch':5,'example_jp':'奨学金を受けている。','example_vi':'Tôi đang nhận học bổng.'},
# === 語 ===
  {'id':'外国語','reading':'がいこくご','meaning':'ngoại ngữ','kanji':['語'],'jlpt':'N4','pitch':5,'example_jp':'外国語を勉強する。','example_vi':'Học ngoại ngữ.'},
  {'id':'英語','reading':'えいご','meaning':'tiếng Anh','kanji':['語'],'jlpt':'N5','pitch':0,'example_jp':'英語が話せますか？','example_vi':'Bạn có thể nói tiếng Anh không?'},
  {'id':'母語','reading':'ぼご','meaning':'tiếng mẹ đẻ','kanji':['語'],'jlpt':'N3','pitch':1,'example_jp':'母語は日本語です。','example_vi':'Tiếng mẹ đẻ của tôi là tiếng Nhật.'},
  {'id':'語学','reading':'ごがく','meaning':'học ngoại ngữ, ngôn ngữ học','kanji':['語','学'],'jlpt':'N3','pitch':1,'example_jp':'語学の才能がある。','example_vi':'Có tài năng về ngôn ngữ.'},
  {'id':'単語','reading':'たんご','meaning':'từ đơn, từ vựng','kanji':['語'],'jlpt':'N4','pitch':1,'example_jp':'毎日単語を覚える。','example_vi':'Mỗi ngày học thuộc từ vựng.'},
# === 食 ===
  {'id':'食事','reading':'しょくじ','meaning':'bữa ăn','kanji':['食'],'jlpt':'N5','pitch':3,'example_jp':'一緒に食事しませんか？','example_vi':'Chúng ta cùng ăn nhé?'},
  {'id':'食べ物','reading':'たべもの','meaning':'thức ăn, đồ ăn','kanji':['食'],'jlpt':'N5','pitch':3,'example_jp':'好きな食べ物は何ですか？','example_vi':'Bạn thích ăn gì?'},
  {'id':'食料','reading':'しょくりょう','meaning':'lương thực, thực phẩm','kanji':['食'],'jlpt':'N3','pitch':0,'example_jp':'食料を備蓄する。','example_vi':'Dự trữ lương thực.'},
  {'id':'外食','reading':'がいしょく','meaning':'ăn ngoài, ăn hàng','kanji':['食'],'jlpt':'N3','pitch':0,'example_jp':'最近外食が多い。','example_vi':'Gần đây tôi hay ăn ngoài.'},
  {'id':'食欲','reading':'しょくよく','meaning':'cảm giác thèm ăn','kanji':['食'],'jlpt':'N3','pitch':0,'example_jp':'食欲がない。','example_vi':'Không có cảm giác thèm ăn.'},
  {'id':'飲食','reading':'いんしょく','meaning':'ăn uống','kanji':['食','飲'],'jlpt':'N3','pitch':1,'example_jp':'飲食店を経営する。','example_vi':'Kinh doanh nhà hàng ăn uống.'},
# === 車 ===
  {'id':'電車','reading':'でんしゃ','meaning':'tàu điện, xe lửa','kanji':['車'],'jlpt':'N5','pitch':0,'example_jp':'電車で学校へ行く。','example_vi':'Đi học bằng tàu điện.'},
  {'id':'自動車','reading':'じどうしゃ','meaning':'ô tô, xe hơi','kanji':['車'],'jlpt':'N4','pitch':3,'example_jp':'自動車を運転する。','example_vi':'Lái xe ô tô.'},
  {'id':'駐車場','reading':'ちゅうしゃじょう','meaning':'bãi đỗ xe','kanji':['車'],'jlpt':'N4','pitch':4,'example_jp':'駐車場に止めてください。','example_vi':'Hãy đỗ xe ở bãi đỗ xe.'},
  {'id':'自転車','reading':'じてんしゃ','meaning':'xe đạp','kanji':['車'],'jlpt':'N5','pitch':3,'example_jp':'自転車で通学している。','example_vi':'Tôi đi xe đạp đến trường.'},
  {'id':'車両','reading':'しゃりょう','meaning':'toa tàu, phương tiện','kanji':['車'],'jlpt':'N3','pitch':0,'example_jp':'この車両は禁煙です。','example_vi':'Toa tàu này cấm hút thuốc.'},
# === 口 ===
  {'id':'入口','reading':'いりぐち','meaning':'lối vào, cửa vào','kanji':['口'],'jlpt':'N5','pitch':0,'example_jp':'入口はどこですか？','example_vi':'Lối vào ở đâu?'},
  {'id':'出口','reading':'でぐち','meaning':'lối ra, cửa ra','kanji':['口'],'jlpt':'N5','pitch':0,'example_jp':'出口を探している。','example_vi':'Tôi đang tìm lối ra.'},
  {'id':'窓口','reading':'まどぐち','meaning':'quầy giao dịch','kanji':['口'],'jlpt':'N4','pitch':3,'example_jp':'窓口で手続きをする。','example_vi':'Làm thủ tục ở quầy giao dịch.'},
  {'id':'口調','reading':'くちょう','meaning':'giọng điệu, cách nói','kanji':['口'],'jlpt':'N3','pitch':0,'example_jp':'丁寧な口調で話す。','example_vi':'Nói chuyện với giọng lịch sự.'},
  {'id':'人口','reading':'じんこう','meaning':'dân số','kanji':['口','人'],'jlpt':'N4','pitch':0,'example_jp':'東京の人口は多い。','example_vi':'Dân số Tokyo rất đông.'},
# === 手 ===
  {'id':'手紙','reading':'てがみ','meaning':'thư (bức thư)','kanji':['手'],'jlpt':'N5','pitch':0,'example_jp':'手紙を書きます。','example_vi':'Tôi viết thư.'},
  {'id':'拍手','reading':'はくしゅ','meaning':'tiếng vỗ tay','kanji':['手'],'jlpt':'N4','pitch':1,'example_jp':'拍手をしてください。','example_vi':'Hãy vỗ tay nào.'},
  {'id':'握手','reading':'あくしゅ','meaning':'bắt tay','kanji':['手'],'jlpt':'N4','pitch':1,'example_jp':'握手をしましょう。','example_vi':'Chúng ta bắt tay nhé.'},
  {'id':'手伝う','reading':'てつだう','meaning':'giúp đỡ, phụ giúp','kanji':['手'],'jlpt':'N5','pitch':3,'example_jp':'手伝ってください。','example_vi':'Hãy giúp tôi.'},
  {'id':'相手','reading':'あいて','meaning':'đối phương, người kia','kanji':['手'],'jlpt':'N3','pitch':3,'example_jp':'相手の気持ちを考える。','example_vi':'Suy nghĩ đến cảm xúc của đối phương.'},
  {'id':'手術','reading':'しゅじゅつ','meaning':'phẫu thuật, ca mổ','kanji':['手'],'jlpt':'N3','pitch':1,'example_jp':'手術を受けた。','example_vi':'Tôi đã phẫu thuật.'},
  {'id':'選手','reading':'せんしゅ','meaning':'vận động viên, cầu thủ','kanji':['手'],'jlpt':'N4','pitch':1,'example_jp':'オリンピック選手を目指す。','example_vi':'Phấn đấu trở thành vận động viên Olympic.'},
# === 目 ===
  {'id':'目的','reading':'もくてき','meaning':'mục đích','kanji':['目'],'jlpt':'N3','pitch':0,'example_jp':'目的を持って行動する。','example_vi':'Hành động với mục đích rõ ràng.'},
  {'id':'注目','reading':'ちゅうもく','meaning':'sự chú ý, sự quan tâm','kanji':['目'],'jlpt':'N3','pitch':0,'example_jp':'世界中から注目されている。','example_vi':'Được cả thế giới chú ý.'},
  {'id':'目標','reading':'もくひょう','meaning':'mục tiêu','kanji':['目'],'jlpt':'N3','pitch':0,'example_jp':'目標を達成した。','example_vi':'Đã đạt được mục tiêu.'},
  {'id':'一目','reading':'ひとめ','meaning':'một cái nhìn, nhìn lướt qua','kanji':['目','一'],'jlpt':'N4','pitch':0,'example_jp':'一目で気に入った。','example_vi':'Nhìn một cái là thích ngay.'},
# === 気 ===
  {'id':'天気','reading':'てんき','meaning':'thời tiết','kanji':['気'],'jlpt':'N5','pitch':1,'example_jp':'今日の天気は晴れです。','example_vi':'Hôm nay trời nắng.'},
  {'id':'元気','reading':'げんき','meaning':'khỏe mạnh, năng động','kanji':['気'],'jlpt':'N5','pitch':1,'example_jp':'元気ですか？','example_vi':'Bạn có khỏe không?'},
  {'id':'気持ち','reading':'きもち','meaning':'cảm xúc, cảm giác','kanji':['気'],'jlpt':'N4','pitch':3,'example_jp':'今日は気持ちがいい。','example_vi':'Hôm nay tôi cảm thấy dễ chịu.'},
  {'id':'気温','reading':'きおん','meaning':'nhiệt độ không khí','kanji':['気'],'jlpt':'N4','pitch':0,'example_jp':'気温が急に下がった。','example_vi':'Nhiệt độ đột ngột giảm.'},
  {'id':'空気','reading':'くうき','meaning':'không khí','kanji':['気'],'jlpt':'N4','pitch':1,'example_jp':'空気がきれいな場所だ。','example_vi':'Đây là nơi không khí trong lành.'},
  {'id':'雰囲気','reading':'ふんいき','meaning':'không khí, bầu không khí','kanji':['気'],'jlpt':'N3','pitch':0,'example_jp':'素敵な雰囲気のお店だ。','example_vi':'Quán có không khí tuyệt vời.'},
  {'id':'人気','reading':'にんき','meaning':'nổi tiếng, được yêu thích','kanji':['気','人'],'jlpt':'N4','pitch':1,'example_jp':'この歌手は人気があります。','example_vi':'Ca sĩ này rất nổi tiếng.'},
  {'id':'本気','reading':'ほんき','meaning':'nghiêm túc, thật tâm','kanji':['気','本'],'jlpt':'N3','pitch':1,'example_jp':'本気で取り組む。','example_vi':'Thật tâm nghiêm túc làm.'},
# === 言 ===
  {'id':'言葉','reading':'ことば','meaning':'lời nói, ngôn ngữ, từ ngữ','kanji':['言'],'jlpt':'N4','pitch':3,'example_jp':'言葉を大切にする。','example_vi':'Trân trọng lời nói.'},
  {'id':'言語','reading':'げんご','meaning':'ngôn ngữ','kanji':['言'],'jlpt':'N3','pitch':1,'example_jp':'言語を学ぶのが好きだ。','example_vi':'Tôi thích học ngôn ngữ.'},
  {'id':'発言','reading':'はつげん','meaning':'phát biểu, lên tiếng','kanji':['言'],'jlpt':'N3','pitch':0,'example_jp':'会議で発言する。','example_vi':'Phát biểu trong cuộc họp.'},
  {'id':'伝言','reading':'でんごん','meaning':'lời nhắn, tin nhắn','kanji':['言'],'jlpt':'N4','pitch':0,'example_jp':'伝言を頼む。','example_vi':'Nhờ nhắn tin giúp.'},
  {'id':'名言','reading':'めいげん','meaning':'câu nói hay, danh ngôn','kanji':['言','名'],'jlpt':'N3','pitch':0,'example_jp':'有名な名言を覚える。','example_vi':'Ghi nhớ câu danh ngôn nổi tiếng.'},
# === 見 ===
  {'id':'見物','reading':'けんぶつ','meaning':'ngắm, tham quan','kanji':['見'],'jlpt':'N4','pitch':1,'example_jp':'お祭りの見物に行く。','example_vi':'Đi xem lễ hội.'},
  {'id':'意見','reading':'いけん','meaning':'ý kiến','kanji':['見'],'jlpt':'N4','pitch':1,'example_jp':'意見を聞かせてください。','example_vi':'Hãy cho tôi biết ý kiến của bạn.'},
  {'id':'見学','reading':'けんがく','meaning':'tham quan (để học hỏi)','kanji':['見','学'],'jlpt':'N4','pitch':0,'example_jp':'工場見学に行く。','example_vi':'Đi tham quan nhà máy.'},
  {'id':'外見','reading':'がいけん','meaning':'vẻ ngoài, ngoại hình','kanji':['見'],'jlpt':'N3','pitch':1,'example_jp':'外見より中身が大切だ。','example_vi':'Nội tâm quan trọng hơn vẻ ngoài.'},
# === 行 ===
  {'id':'旅行','reading':'りょこう','meaning':'du lịch, chuyến đi','kanji':['行'],'jlpt':'N5','pitch':0,'example_jp':'旅行が好きです。','example_vi':'Tôi thích du lịch.'},
  {'id':'銀行','reading':'ぎんこう','meaning':'ngân hàng','kanji':['行'],'jlpt':'N5','pitch':0,'example_jp':'銀行でお金を引き出す。','example_vi':'Rút tiền ở ngân hàng.'},
  {'id':'行動','reading':'こうどう','meaning':'hành động, hành vi','kanji':['行'],'jlpt':'N3','pitch':0,'example_jp':'すぐに行動に移す。','example_vi':'Chuyển ngay sang hành động.'},
  {'id':'進行','reading':'しんこう','meaning':'tiến hành, tiến triển','kanji':['行'],'jlpt':'N3','pitch':0,'example_jp':'計画が順調に進行している。','example_vi':'Kế hoạch đang tiến hành thuận lợi.'},
  {'id':'行方','reading':'ゆくえ','meaning':'nơi đến, tung tích','kanji':['行'],'jlpt':'N3','pitch':0,'example_jp':'行方が分からない。','example_vi':'Không biết tung tích ở đâu.'},
  {'id':'流行','reading':'りゅうこう','meaning':'thịnh hành, mốt','kanji':['行'],'jlpt':'N3','pitch':0,'example_jp':'今年の流行を追う。','example_vi':'Theo dõi xu hướng năm nay.'},
# === 来 ===
  {'id':'来週','reading':'らいしゅう','meaning':'tuần sau','kanji':['来'],'jlpt':'N5','pitch':0,'example_jp':'来週また来てください。','example_vi':'Tuần sau hãy đến lại nhé.'},
  {'id':'将来','reading':'しょうらい','meaning':'tương lai','kanji':['来'],'jlpt':'N4','pitch':0,'example_jp':'将来の夢は医者です。','example_vi':'Ước mơ tương lai là bác sĩ.'},
  {'id':'由来','reading':'ゆらい','meaning':'nguồn gốc, xuất xứ','kanji':['来'],'jlpt':'N3','pitch':0,'example_jp':'この言葉の由来を調べる。','example_vi':'Tìm hiểu nguồn gốc từ này.'},
  {'id':'本来','reading':'ほんらい','meaning':'vốn dĩ, ban đầu','kanji':['来','本'],'jlpt':'N3','pitch':1,'example_jp':'本来の目的に戻る。','example_vi':'Quay về mục đích ban đầu.'},
# === 出 ===
  {'id':'出発','reading':'しゅっぱつ','meaning':'khởi hành, xuất phát','kanji':['出'],'jlpt':'N5','pitch':0,'example_jp':'朝7時に出発します。','example_vi':'Tôi khởi hành lúc 7 giờ sáng.'},
  {'id':'出身','reading':'しゅっしん','meaning':'xuất thân, quê quán','kanji':['出'],'jlpt':'N4','pitch':0,'example_jp':'東京出身です。','example_vi':'Tôi quê ở Tokyo.'},
  {'id':'提出','reading':'ていしゅつ','meaning':'nộp, đệ trình','kanji':['出'],'jlpt':'N4','pitch':0,'example_jp':'レポートを提出する。','example_vi':'Nộp báo cáo.'},
  {'id':'外出','reading':'がいしゅつ','meaning':'ra ngoài, đi ra ngoài','kanji':['出'],'jlpt':'N4','pitch':0,'example_jp':'今日は外出しない。','example_vi':'Hôm nay tôi không ra ngoài.'},
  {'id':'輸出','reading':'ゆしゅつ','meaning':'xuất khẩu','kanji':['出'],'jlpt':'N3','pitch':0,'example_jp':'自動車を輸出している。','example_vi':'Xuất khẩu ô tô.'},
  {'id':'演出','reading':'えんしゅつ','meaning':'dàn dựng, chỉ đạo nghệ thuật','kanji':['出'],'jlpt':'N3','pitch':0,'example_jp':'素晴らしい演出だった。','example_vi':'Cách dàn dựng thật tuyệt vời.'},
# === 入 ===
  {'id':'輸入','reading':'ゆにゅう','meaning':'nhập khẩu','kanji':['入'],'jlpt':'N3','pitch':0,'example_jp':'石油を輸入する。','example_vi':'Nhập khẩu dầu mỏ.'},
  {'id':'収入','reading':'しゅうにゅう','meaning':'thu nhập','kanji':['入'],'jlpt':'N3','pitch':0,'example_jp':'収入を増やしたい。','example_vi':'Tôi muốn tăng thu nhập.'},
  {'id':'導入','reading':'どうにゅう','meaning':'đưa vào, áp dụng','kanji':['入'],'jlpt':'N3','pitch':0,'example_jp':'新システムを導入する。','example_vi':'Áp dụng hệ thống mới.'},
  {'id':'入社','reading':'にゅうしゃ','meaning':'vào làm công ty','kanji':['入'],'jlpt':'N4','pitch':0,'example_jp':'春に入社します。','example_vi':'Mùa xuân tôi vào công ty.'},
# === 会 ===
  {'id':'会社','reading':'かいしゃ','meaning':'công ty','kanji':['会'],'jlpt':'N5','pitch':1,'example_jp':'会社で働いています。','example_vi':'Tôi làm việc ở công ty.'},
  {'id':'会議','reading':'かいぎ','meaning':'cuộc họp, hội nghị','kanji':['会'],'jlpt':'N4','pitch':1,'example_jp':'午後に会議がある。','example_vi':'Buổi chiều có cuộc họp.'},
  {'id':'社会','reading':'しゃかい','meaning':'xã hội','kanji':['会'],'jlpt':'N4','pitch':1,'example_jp':'社会のために働く。','example_vi':'Làm việc vì xã hội.'},
  {'id':'機会','reading':'きかい','meaning':'cơ hội','kanji':['会'],'jlpt':'N3','pitch':1,'example_jp':'良い機会を逃した。','example_vi':'Tôi đã bỏ lỡ cơ hội tốt.'},
  {'id':'出会い','reading':'であい','meaning':'sự gặp gỡ','kanji':['会'],'jlpt':'N3','pitch':0,'example_jp':'素晴らしい出会いがあった。','example_vi':'Có một cuộc gặp gỡ tuyệt vời.'},
  {'id':'再会','reading':'さいかい','meaning':'gặp lại, tái ngộ','kanji':['会'],'jlpt':'N3','pitch':0,'example_jp':'久しぶりの再会だ。','example_vi':'Lâu ngày mới gặp lại.'},
# === 話 ===
  {'id':'電話','reading':'でんわ','meaning':'điện thoại, gọi điện','kanji':['話'],'jlpt':'N5','pitch':1,'example_jp':'電話してください。','example_vi':'Hãy gọi điện cho tôi.'},
  {'id':'会話','reading':'かいわ','meaning':'hội thoại, đối thoại','kanji':['話','会'],'jlpt':'N4','pitch':1,'example_jp':'日常会話を練習する。','example_vi':'Luyện tập hội thoại hằng ngày.'},
  {'id':'話題','reading':'わだい','meaning':'chủ đề, đề tài','kanji':['話'],'jlpt':'N3','pitch':0,'example_jp':'最近の話題は何ですか？','example_vi':'Chủ đề gần đây là gì?'},
  {'id':'童話','reading':'どうわ','meaning':'truyện cổ tích, truyện tranh trẻ em','kanji':['話'],'jlpt':'N4','pitch':1,'example_jp':'童話を読んで育った。','example_vi':'Tôi lớn lên cùng truyện cổ tích.'},
# === 読 ===
  {'id':'読書','reading':'どくしょ','meaning':'đọc sách','kanji':['読'],'jlpt':'N4','pitch':1,'example_jp':'読書が趣味です。','example_vi':'Đọc sách là sở thích của tôi.'},
  {'id':'読者','reading':'どくしゃ','meaning':'độc giả','kanji':['読'],'jlpt':'N3','pitch':1,'example_jp':'読者からの意見を集める。','example_vi':'Thu thập ý kiến từ độc giả.'},
  {'id':'音読','reading':'おんどく','meaning':'đọc to, đọc thành tiếng','kanji':['読'],'jlpt':'N4','pitch':1,'example_jp':'本を音読する。','example_vi':'Đọc to quyển sách.'},
# === 書 ===
  {'id':'辞書','reading':'じしょ','meaning':'từ điển','kanji':['書'],'jlpt':'N5','pitch':1,'example_jp':'辞書で単語を調べる。','example_vi':'Tra từ trong từ điển.'},
  {'id':'教科書','reading':'きょうかしょ','meaning':'sách giáo khoa','kanji':['書'],'jlpt':'N5','pitch':5,'example_jp':'教科書を忘れた。','example_vi':'Tôi quên sách giáo khoa.'},
  {'id':'書類','reading':'しょるい','meaning':'tài liệu, văn bản','kanji':['書'],'jlpt':'N3','pitch':0,'example_jp':'書類を提出する。','example_vi':'Nộp tài liệu.'},
  {'id':'読み書き','reading':'よみかき','meaning':'đọc và viết','kanji':['書','読'],'jlpt':'N4','pitch':4,'example_jp':'読み書きができる。','example_vi':'Có thể đọc và viết.'},
# === 友 ===
  {'id':'友達','reading':'ともだち','meaning':'bạn bè','kanji':['友'],'jlpt':'N5','pitch':0,'example_jp':'友達と遊びます。','example_vi':'Tôi chơi với bạn bè.'},
  {'id':'友人','reading':'ゆうじん','meaning':'bạn bè (lịch sự hơn)','kanji':['友'],'jlpt':'N4','pitch':0,'example_jp':'大切な友人がいる。','example_vi':'Tôi có người bạn quý giá.'},
  {'id':'親友','reading':'しんゆう','meaning':'bạn thân, người bạn tri kỷ','kanji':['友'],'jlpt':'N3','pitch':0,'example_jp':'親友に相談する。','example_vi':'Tâm sự với bạn thân.'},
  {'id':'友好','reading':'ゆうこう','meaning':'hữu nghị, thân thiện','kanji':['友'],'jlpt':'N3','pitch':0,'example_jp':'友好関係を築く。','example_vi':'Xây dựng quan hệ hữu nghị.'},
# === 名 ===
  {'id':'名前','reading':'なまえ','meaning':'tên, họ tên','kanji':['名'],'jlpt':'N5','pitch':0,'example_jp':'お名前は何ですか？','example_vi':'Tên bạn là gì?'},
  {'id':'有名','reading':'ゆうめい','meaning':'nổi tiếng','kanji':['名'],'jlpt':'N4','pitch':0,'example_jp':'この店は有名です。','example_vi':'Quán này rất nổi tiếng.'},
  {'id':'名刺','reading':'めいし','meaning':'danh thiếp','kanji':['名'],'jlpt':'N4','pitch':1,'example_jp':'名刺を交換する。','example_vi':'Trao đổi danh thiếp.'},
  {'id':'名所','reading':'めいしょ','meaning':'danh lam thắng cảnh','kanji':['名'],'jlpt':'N4','pitch':3,'example_jp':'京都の名所を回る。','example_vi':'Tham quan các danh lam ở Kyoto.'},
  {'id':'名人','reading':'めいじん','meaning':'bậc thầy, cao thủ','kanji':['名'],'jlpt':'N3','pitch':0,'example_jp':'料理の名人だ。','example_vi':'Bậc thầy về nấu ăn.'},
# === 道 ===
  {'id':'道路','reading':'どうろ','meaning':'đường xá, đường bộ','kanji':['道'],'jlpt':'N4','pitch':1,'example_jp':'道路工事中です。','example_vi':'Đường đang thi công.'},
  {'id':'近道','reading':'ちかみち','meaning':'đường tắt','kanji':['道'],'jlpt':'N4','pitch':0,'example_jp':'近道を教えてください。','example_vi':'Hãy chỉ đường tắt cho tôi.'},
  {'id':'柔道','reading':'じゅうどう','meaning':'Judo (môn võ)','kanji':['道'],'jlpt':'N4','pitch':0,'example_jp':'柔道を習っている。','example_vi':'Tôi đang học Judo.'},
  {'id':'歩道','reading':'ほどう','meaning':'vỉa hè, đường đi bộ','kanji':['道'],'jlpt':'N4','pitch':0,'example_jp':'歩道を歩く。','example_vi':'Đi trên vỉa hè.'},
  {'id':'鉄道','reading':'てつどう','meaning':'đường sắt, xe lửa','kanji':['道'],'jlpt':'N3','pitch':0,'example_jp':'鉄道で移動する。','example_vi':'Di chuyển bằng đường sắt.'},
# === 立 ===
  {'id':'立派','reading':'りっぱ','meaning':'xuất sắc, ấn tượng','kanji':['立'],'jlpt':'N4','pitch':0,'example_jp':'立派な建物ですね。','example_vi':'Tòa nhà thật ấn tượng nhỉ.'},
  {'id':'国立','reading':'こくりつ','meaning':'quốc lập, do nhà nước lập','kanji':['立','国'],'jlpt':'N4','pitch':0,'example_jp':'国立博物館に行く。','example_vi':'Đến bảo tàng quốc gia.'},
  {'id':'私立','reading':'しりつ','meaning':'tư lập, do tư nhân lập','kanji':['立'],'jlpt':'N4','pitch':0,'example_jp':'私立学校に通う。','example_vi':'Theo học trường tư.'},
  {'id':'自立','reading':'じりつ','meaning':'tự lập, độc lập','kanji':['立'],'jlpt':'N3','pitch':0,'example_jp':'自立した生活を送る。','example_vi':'Sống cuộc sống tự lập.'},
# === 本 ===
  {'id':'基本','reading':'きほん','meaning':'cơ bản, nền tảng','kanji':['本'],'jlpt':'N4','pitch':2,'example_jp':'基本から学ぶ。','example_vi':'Học từ cơ bản.'},
  {'id':'本棚','reading':'ほんだな','meaning':'giá sách','kanji':['本'],'jlpt':'N5','pitch':3,'example_jp':'本棚に本が並んでいる。','example_vi':'Sách xếp trên giá sách.'},
  {'id':'本屋','reading':'ほんや','meaning':'hiệu sách, nhà sách','kanji':['本'],'jlpt':'N5','pitch':1,'example_jp':'本屋で新しい本を買った。','example_vi':'Tôi mua sách mới ở nhà sách.'},
  {'id':'本物','reading':'ほんもの','meaning':'đồ thật, hàng thật','kanji':['本'],'jlpt':'N3','pitch':0,'example_jp':'本物のダイヤモンドだ。','example_vi':'Kim cương thật đấy.'},
  {'id':'見本','reading':'みほん','meaning':'mẫu, hàng mẫu','kanji':['本'],'jlpt':'N4','pitch':0,'example_jp':'見本を見せてください。','example_vi':'Hãy cho tôi xem mẫu.'},
# === 白 ===
  {'id':'白い','reading':'しろい','meaning':'màu trắng','kanji':['白'],'jlpt':'N5','pitch':2,'example_jp':'白いシャツを着ている。','example_vi':'Đang mặc áo sơ mi trắng.'},
  {'id':'白黒','reading':'しろくろ','meaning':'đen trắng','kanji':['白'],'jlpt':'N4','pitch':3,'example_jp':'白黒写真が好きだ。','example_vi':'Tôi thích ảnh đen trắng.'},
  {'id':'告白','reading':'こくはく','meaning':'thú nhận, bày tỏ tình cảm','kanji':['白'],'jlpt':'N3','pitch':0,'example_jp':'好きな人に告白した。','example_vi':'Tôi đã tỏ tình với người mình thích.'},
  {'id':'空白','reading':'くうはく','meaning':'khoảng trống, chỗ trống','kanji':['白'],'jlpt':'N3','pitch':0,'example_jp':'空白を埋める。','example_vi':'Điền vào chỗ trống.'},
# === 半 ===
  {'id':'半分','reading':'はんぶん','meaning':'một nửa','kanji':['半'],'jlpt':'N5','pitch':3,'example_jp':'半分食べた。','example_vi':'Tôi đã ăn một nửa.'},
  {'id':'後半','reading':'こうはん','meaning':'nửa sau, hiệp hai','kanji':['半'],'jlpt':'N3','pitch':0,'example_jp':'後半に点を入れた。','example_vi':'Ghi bàn ở hiệp hai.'},
  {'id':'前半','reading':'ぜんはん','meaning':'nửa đầu, hiệp một','kanji':['半'],'jlpt':'N3','pitch':0,'example_jp':'前半はリードしていた。','example_vi':'Nửa đầu họ đang dẫn điểm.'},
  {'id':'半年','reading':'はんとし','meaning':'nửa năm','kanji':['半'],'jlpt':'N4','pitch':2,'example_jp':'半年間日本に住んでいた。','example_vi':'Tôi đã sống ở Nhật nửa năm.'},
# === 分 ===
  {'id':'自分','reading':'じぶん','meaning':'bản thân, tự mình','kanji':['分'],'jlpt':'N5','pitch':0,'example_jp':'自分で考えてください。','example_vi':'Hãy tự mình suy nghĩ.'},
  {'id':'十分','reading':'じゅうぶん','meaning':'đầy đủ, đủ rồi','kanji':['分'],'jlpt':'N4','pitch':0,'example_jp':'十分な時間がある。','example_vi':'Có đủ thời gian.'},
  {'id':'気分','reading':'きぶん','meaning':'tâm trạng, cảm giác','kanji':['分','気'],'jlpt':'N4','pitch':1,'example_jp':'気分が悪い。','example_vi':'Tôi cảm thấy không khỏe.'},
  {'id':'部分','reading':'ぶぶん','meaning':'phần, bộ phận','kanji':['分'],'jlpt':'N3','pitch':0,'example_jp':'一部分だけ直す。','example_vi':'Sửa chỉ một phần.'},
# === 聞 ===
  {'id':'新聞','reading':'しんぶん','meaning':'báo, tờ báo','kanji':['聞'],'jlpt':'N5','pitch':0,'example_jp':'毎朝新聞を読む。','example_vi':'Mỗi sáng đọc báo.'},
  {'id':'聞こえる','reading':'きこえる','meaning':'nghe thấy được','kanji':['聞'],'jlpt':'N4','pitch':0,'example_jp':'音楽が聞こえる。','example_vi':'Nghe thấy tiếng nhạc.'},
# === 買 ===
  {'id':'買い物','reading':'かいもの','meaning':'mua sắm','kanji':['買'],'jlpt':'N5','pitch':0,'example_jp':'買い物に行きます。','example_vi':'Tôi đi mua sắm.'},
  {'id':'購買','reading':'こうばい','meaning':'mua sắm, căng tin','kanji':['買'],'jlpt':'N3','pitch':0,'example_jp':'学校の購買でパンを買う。','example_vi':'Mua bánh mì ở căng tin trường.'},
# === 売 ===
  {'id':'売り場','reading':'うりば','meaning':'quầy bán hàng','kanji':['売'],'jlpt':'N4','pitch':0,'example_jp':'お菓子売り場はどこですか？','example_vi':'Quầy bánh kẹo ở đâu?'},
  {'id':'販売','reading':'はんばい','meaning':'bán hàng, kinh doanh bán lẻ','kanji':['売'],'jlpt':'N3','pitch':0,'example_jp':'新商品を販売する。','example_vi':'Bán sản phẩm mới.'},
  {'id':'安売り','reading':'やすうり','meaning':'bán rẻ, giảm giá','kanji':['売'],'jlpt':'N4','pitch':0,'example_jp':'スーパーで安売りをしている。','example_vi':'Siêu thị đang giảm giá.'},
# === 休 ===
  {'id':'夏休み','reading':'なつやすみ','meaning':'nghỉ hè','kanji':['休'],'jlpt':'N5','pitch':5,'example_jp':'夏休みに旅行する。','example_vi':'Du lịch trong kỳ nghỉ hè.'},
  {'id':'冬休み','reading':'ふゆやすみ','meaning':'nghỉ đông','kanji':['休'],'jlpt':'N5','pitch':5,'example_jp':'冬休みに帰省する。','example_vi':'Về quê trong kỳ nghỉ đông.'},
  {'id':'昼休み','reading':'ひるやすみ','meaning':'nghỉ trưa','kanji':['休'],'jlpt':'N5','pitch':5,'example_jp':'昼休みに食事する。','example_vi':'Ăn cơm trong giờ nghỉ trưa.'},
  {'id':'休憩','reading':'きゅうけい','meaning':'nghỉ giải lao','kanji':['休'],'jlpt':'N4','pitch':0,'example_jp':'少し休憩しましょう。','example_vi':'Hãy nghỉ một chút nhé.'},
# === 高 ===
  {'id':'高校','reading':'こうこう','meaning':'trường trung học phổ thông','kanji':['高'],'jlpt':'N5','pitch':0,'example_jp':'高校で英語を勉強した。','example_vi':'Tôi học tiếng Anh ở THPT.'},
  {'id':'高校生','reading':'こうこうせい','meaning':'học sinh trung học phổ thông','kanji':['高'],'jlpt':'N5','pitch':5,'example_jp':'高校生のとき部活をした。','example_vi':'Hồi học THPT tôi tham gia câu lạc bộ.'},
  {'id':'最高','reading':'さいこう','meaning':'tuyệt vời nhất, cao nhất','kanji':['高'],'jlpt':'N4','pitch':0,'example_jp':'今日は最高の天気だ。','example_vi':'Hôm nay thời tiết tuyệt vời nhất.'},
  {'id':'高速','reading':'こうそく','meaning':'tốc độ cao, đường cao tốc','kanji':['高'],'jlpt':'N3','pitch':0,'example_jp':'高速道路を走る。','example_vi':'Chạy trên đường cao tốc.'},
  {'id':'高齢','reading':'こうれい','meaning':'tuổi cao, người cao tuổi','kanji':['高'],'jlpt':'N3','pitch':0,'example_jp':'高齢化社会が進む。','example_vi':'Xã hội già hóa đang tiến triển.'},
# === 安 ===
  {'id':'安心','reading':'あんしん','meaning':'yên tâm, an tâm','kanji':['安'],'jlpt':'N4','pitch':0,'example_jp':'安心してください。','example_vi':'Hãy yên tâm.'},
  {'id':'安全','reading':'あんぜん','meaning':'an toàn','kanji':['安'],'jlpt':'N4','pitch':0,'example_jp':'安全運転をする。','example_vi':'Lái xe an toàn.'},
  {'id':'不安','reading':'ふあん','meaning':'lo lắng, bất an','kanji':['安'],'jlpt':'N4','pitch':0,'example_jp':'試験が不安だ。','example_vi':'Tôi lo lắng về kỳ thi.'},
  {'id':'安定','reading':'あんてい','meaning':'ổn định','kanji':['安'],'jlpt':'N3','pitch':0,'example_jp':'安定した仕事を求める。','example_vi':'Tìm kiếm công việc ổn định.'},
# === 新 ===
  {'id':'新幹線','reading':'しんかんせん','meaning':'tàu siêu tốc Shinkansen','kanji':['新'],'jlpt':'N5','pitch':5,'example_jp':'新幹線で大阪へ行く。','example_vi':'Đi Osaka bằng Shinkansen.'},
  {'id':'最新','reading':'さいしん','meaning':'mới nhất, hiện đại nhất','kanji':['新'],'jlpt':'N3','pitch':0,'example_jp':'最新のスマホを買った。','example_vi':'Tôi mua điện thoại mới nhất.'},
  {'id':'新鮮','reading':'しんせん','meaning':'tươi, mới mẻ','kanji':['新'],'jlpt':'N3','pitch':0,'example_jp':'新鮮な野菜を買う。','example_vi':'Mua rau tươi.'},
  {'id':'新年','reading':'しんねん','meaning':'năm mới','kanji':['新','年'],'jlpt':'N5','pitch':1,'example_jp':'新年あけましておめでとう。','example_vi':'Chúc mừng năm mới.'},
# === 古 ===
  {'id':'古い','reading':'ふるい','meaning':'cũ, xưa, cổ','kanji':['古'],'jlpt':'N5','pitch':2,'example_jp':'古い家に住んでいる。','example_vi':'Tôi sống trong ngôi nhà cũ.'},
  {'id':'古典','reading':'こてん','meaning':'tác phẩm cổ điển','kanji':['古'],'jlpt':'N3','pitch':0,'example_jp':'古典を読む。','example_vi':'Đọc tác phẩm cổ điển.'},
  {'id':'中古','reading':'ちゅうこ','meaning':'đồ cũ, hàng đã qua sử dụng','kanji':['古'],'jlpt':'N3','pitch':0,'example_jp':'中古車を買った。','example_vi':'Tôi mua xe cũ.'},
# === 長 ===
  {'id':'社長','reading':'しゃちょう','meaning':'giám đốc công ty','kanji':['長'],'jlpt':'N4','pitch':0,'example_jp':'社長に報告する。','example_vi':'Báo cáo với giám đốc.'},
  {'id':'身長','reading':'しんちょう','meaning':'chiều cao (người)','kanji':['長'],'jlpt':'N4','pitch':0,'example_jp':'身長が伸びた。','example_vi':'Chiều cao tăng lên.'},
  {'id':'校長','reading':'こうちょう','meaning':'hiệu trưởng','kanji':['長'],'jlpt':'N4','pitch':0,'example_jp':'校長先生の話を聞く。','example_vi':'Nghe lời thầy hiệu trưởng.'},
  {'id':'成長','reading':'せいちょう','meaning':'trưởng thành, phát triển','kanji':['長'],'jlpt':'N3','pitch':0,'example_jp':'子供の成長を見守る。','example_vi':'Dõi theo sự trưởng thành của con.'},
  {'id':'長所','reading':'ちょうしょ','meaning':'ưu điểm, điểm mạnh','kanji':['長'],'jlpt':'N4','pitch':1,'example_jp':'自分の長所を伸ばす。','example_vi':'Phát huy ưu điểm của bản thân.'},
# === 力 ===
  {'id':'努力','reading':'どりょく','meaning':'nỗ lực, cố gắng','kanji':['力'],'jlpt':'N4','pitch':1,'example_jp':'努力すれば夢は叶う。','example_vi':'Nếu nỗ lực, ước mơ sẽ thành sự thật.'},
  {'id':'体力','reading':'たいりょく','meaning':'thể lực, sức mạnh thể chất','kanji':['力'],'jlpt':'N4','pitch':0,'example_jp':'体力をつけたい。','example_vi':'Tôi muốn tăng cường thể lực.'},
  {'id':'能力','reading':'のうりょく','meaning':'năng lực, khả năng','kanji':['力'],'jlpt':'N3','pitch':0,'example_jp':'自分の能力を信じる。','example_vi':'Tin vào năng lực bản thân.'},
  {'id':'協力','reading':'きょうりょく','meaning':'hợp tác, phối hợp','kanji':['力'],'jlpt':'N4','pitch':0,'example_jp':'協力してください。','example_vi':'Hãy hợp tác với tôi.'},
  {'id':'全力','reading':'ぜんりょく','meaning':'toàn lực, hết sức','kanji':['力'],'jlpt':'N3','pitch':2,'example_jp':'全力で頑張ります。','example_vi':'Tôi sẽ cố gắng hết sức.'},
  {'id':'魅力','reading':'みりょく','meaning':'sức hút, sức hấp dẫn','kanji':['力'],'jlpt':'N3','pitch':0,'example_jp':'あの人には魅力がある。','example_vi':'Người đó rất có sức hút.'},
# === 花 ===
  {'id':'花屋','reading':'はなや','meaning':'tiệm hoa','kanji':['花'],'jlpt':'N5','pitch':0,'example_jp':'花屋で花束を買った。','example_vi':'Tôi mua bó hoa ở tiệm hoa.'},
  {'id':'花見','reading':'はなみ','meaning':'ngắm hoa anh đào','kanji':['花'],'jlpt':'N5','pitch':2,'example_jp':'春に花見をする。','example_vi':'Mùa xuân đi ngắm hoa anh đào.'},
  {'id':'生け花','reading':'いけばな','meaning':'nghệ thuật cắm hoa Nhật','kanji':['花'],'jlpt':'N4','pitch':4,'example_jp':'生け花を習っている。','example_vi':'Tôi đang học cắm hoa Nhật.'},
  {'id':'花びら','reading':'はなびら','meaning':'cánh hoa','kanji':['花'],'jlpt':'N4','pitch':3,'example_jp':'桜の花びらが散る。','example_vi':'Cánh hoa anh đào rơi.'},
  {'id':'開花','reading':'かいか','meaning':'nở hoa, khai hoa','kanji':['花'],'jlpt':'N3','pitch':1,'example_jp':'才能が開花した。','example_vi':'Tài năng nở rộ.'},
# === 雨 ===
  {'id':'小雨','reading':'こさめ','meaning':'mưa nhỏ, mưa phùn','kanji':['雨'],'jlpt':'N4','pitch':0,'example_jp':'小雨が降っている。','example_vi':'Đang mưa nhỏ.'},
  {'id':'梅雨','reading':'つゆ','meaning':'mùa mưa (tháng 6-7 ở Nhật)','kanji':['雨'],'jlpt':'N4','pitch':1,'example_jp':'梅雨になると気分が落ちる。','example_vi':'Vào mùa mưa tôi cảm thấy buồn.'},
  {'id':'雨具','reading':'あまぐ','meaning':'đồ dùng khi mưa (ô, áo mưa)','kanji':['雨'],'jlpt':'N4','pitch':0,'example_jp':'雨具を用意する。','example_vi':'Chuẩn bị đồ dùng khi mưa.'},
# === 飲 ===
  {'id':'飲み物','reading':'のみもの','meaning':'đồ uống','kanji':['飲'],'jlpt':'N5','pitch':3,'example_jp':'飲み物は何がいいですか？','example_vi':'Bạn muốn uống gì?'},
  {'id':'飲み会','reading':'のみかい','meaning':'tiệc nhậu, buổi uống bia','kanji':['飲'],'jlpt':'N4','pitch':0,'example_jp':'今夜飲み会がある。','example_vi':'Tối nay có buổi nhậu.'},
# === 右 ===
  {'id':'右手','reading':'みぎて','meaning':'tay phải','kanji':['右','手'],'jlpt':'N5','pitch':3,'example_jp':'右手でペンを持つ。','example_vi':'Cầm bút bằng tay phải.'},
  {'id':'右折','reading':'うせつ','meaning':'rẽ phải','kanji':['右'],'jlpt':'N4','pitch':0,'example_jp':'次の角を右折してください。','example_vi':'Hãy rẽ phải ở góc tiếp theo.'},
  {'id':'左右','reading':'さゆう','meaning':'tả hữu, hai bên trái phải','kanji':['右'],'jlpt':'N4','pitch':1,'example_jp':'左右を確認してから渡る。','example_vi':'Nhìn hai bên trái phải rồi mới sang đường.'},
# === 東/西/南/北 ===
  {'id':'東京','reading':'とうきょう','meaning':'Tokyo (thành phố)','kanji':['東'],'jlpt':'N5','pitch':0,'example_jp':'東京に住んでいます。','example_vi':'Tôi sống ở Tokyo.'},
  {'id':'北海道','reading':'ほっかいどう','meaning':'Hokkaido','kanji':['北'],'jlpt':'N5','pitch':5,'example_jp':'北海道でラーメンを食べた。','example_vi':'Tôi đã ăn ramen ở Hokkaido.'},
  {'id':'南北','reading':'なんぼく','meaning':'Nam Bắc','kanji':['北'],'jlpt':'N4','pitch':1,'example_jp':'南北に分かれている。','example_vi':'Chia thành Nam và Bắc.'},
  {'id':'関西','reading':'かんさい','meaning':'vùng Kansai','kanji':['西'],'jlpt':'N4','pitch':0,'example_jp':'関西弁が好きだ。','example_vi':'Tôi thích tiếng địa phương Kansai.'},
  {'id':'中東','reading':'ちゅうとう','meaning':'Trung Đông','kanji':['東'],'jlpt':'N3','pitch':0,'example_jp':'中東の情勢が不安定だ。','example_vi':'Tình hình Trung Đông không ổn định.'},
# === 毎 ===
  {'id':'毎週','reading':'まいしゅう','meaning':'hàng tuần, mỗi tuần','kanji':['毎'],'jlpt':'N5','pitch':0,'example_jp':'毎週日曜日に運動する。','example_vi':'Tôi tập thể dục mỗi chủ nhật.'},
  {'id':'毎朝','reading':'まいあさ','meaning':'mỗi buổi sáng','kanji':['毎'],'jlpt':'N5','pitch':0,'example_jp':'毎朝ジョギングをする。','example_vi':'Tôi chạy bộ mỗi buổi sáng.'},
  {'id':'毎晩','reading':'まいばん','meaning':'mỗi buổi tối','kanji':['毎'],'jlpt':'N5','pitch':0,'example_jp':'毎晩本を読む。','example_vi':'Mỗi tối tôi đọc sách.'},
# === 何 ===
  {'id':'何か','reading':'なにか','meaning':'điều gì đó, có gì đó','kanji':['何'],'jlpt':'N5','pitch':1,'example_jp':'何か食べますか？','example_vi':'Bạn ăn gì không?'},
  {'id':'何も','reading':'なにも','meaning':'không có gì (phủ định)','kanji':['何'],'jlpt':'N5','pitch':1,'example_jp':'何も食べていない。','example_vi':'Tôi không ăn gì cả.'},
  {'id':'何回','reading':'なんかい','meaning':'bao nhiêu lần','kanji':['何'],'jlpt':'N5','pitch':0,'example_jp':'何回練習しましたか？','example_vi':'Bạn đã luyện tập bao nhiêu lần?'},
  {'id':'何人','reading':'なんにん','meaning':'bao nhiêu người','kanji':['何','人'],'jlpt':'N5','pitch':0,'example_jp':'何人来ますか？','example_vi':'Bao nhiêu người sẽ đến?'},
# === N4 vocabulary additions ===
# 体 ===
  {'id':'体育','reading':'たいいく','meaning':'thể dục (môn học)','kanji':['体'],'jlpt':'N4','pitch':0,'example_jp':'体育の授業がある。','example_vi':'Có tiết thể dục.'},
  {'id':'体重','reading':'たいじゅう','meaning':'cân nặng','kanji':['体'],'jlpt':'N4','pitch':0,'example_jp':'体重を量る。','example_vi':'Cân trọng lượng.'},
  {'id':'具体的','reading':'ぐたいてき','meaning':'cụ thể','kanji':['体'],'jlpt':'N3','pitch':0,'example_jp':'具体的に説明する。','example_vi':'Giải thích một cách cụ thể.'},
  {'id':'体験','reading':'たいけん','meaning':'trải nghiệm thực tế','kanji':['体'],'jlpt':'N3','pitch':0,'example_jp':'海外体験をする。','example_vi':'Có trải nghiệm ở nước ngoài.'},
  {'id':'身体','reading':'しんたい','meaning':'cơ thể, thân thể','kanji':['体'],'jlpt':'N3','pitch':1,'example_jp':'身体検査を受ける。','example_vi':'Đi khám sức khỏe.'},
# 心 ===
  {'id':'心配','reading':'しんぱい','meaning':'lo lắng, lo ngại','kanji':['心'],'jlpt':'N4','pitch':0,'example_jp':'心配しないでください。','example_vi':'Đừng lo lắng.'},
  {'id':'関心','reading':'かんしん','meaning':'quan tâm, chú ý','kanji':['心'],'jlpt':'N3','pitch':0,'example_jp':'環境問題に関心がある。','example_vi':'Tôi quan tâm đến vấn đề môi trường.'},
  {'id':'熱心','reading':'ねっしん','meaning':'nhiệt tình, chăm chỉ','kanji':['心'],'jlpt':'N3','pitch':0,'example_jp':'熱心に勉強する。','example_vi':'Học hành chăm chỉ.'},
  {'id':'中心','reading':'ちゅうしん','meaning':'trung tâm','kanji':['心','中'],'jlpt':'N3','pitch':0,'example_jp':'事件の中心にいる。','example_vi':'Ở trung tâm sự kiện.'},
# 思 ===
  {'id':'思い出','reading':'おもいで','meaning':'kỷ niệm, ký ức','kanji':['思'],'jlpt':'N4','pitch':0,'example_jp':'楽しい思い出がある。','example_vi':'Có những kỷ niệm vui.'},
  {'id':'思想','reading':'しそう','meaning':'tư tưởng, suy nghĩ','kanji':['思'],'jlpt':'N3','pitch':0,'example_jp':'自由な思想を持つ。','example_vi':'Có tư tưởng tự do.'},
# 知 ===
  {'id':'知識','reading':'ちしき','meaning':'kiến thức','kanji':['知'],'jlpt':'N3','pitch':0,'example_jp':'知識を深める。','example_vi':'Trau dồi kiến thức.'},
  {'id':'知人','reading':'ちじん','meaning':'người quen biết','kanji':['知','人'],'jlpt':'N4','pitch':1,'example_jp':'知人に会った。','example_vi':'Tôi gặp người quen.'},
  {'id':'無知','reading':'むち','meaning':'vô kiến thức, thiếu hiểu biết','kanji':['知'],'jlpt':'N3','pitch':1,'example_jp':'無知を恥じる。','example_vi':'Xấu hổ vì sự thiếu hiểu biết.'},
# 思/考 ===
  {'id':'考え方','reading':'かんがえかた','meaning':'cách nghĩ, quan điểm','kanji':['考'],'jlpt':'N3','pitch':5,'example_jp':'柔軟な考え方が大切だ。','example_vi':'Cách nghĩ linh hoạt rất quan trọng.'},
  {'id':'参考','reading':'さんこう','meaning':'tham khảo','kanji':['考'],'jlpt':'N3','pitch':0,'example_jp':'参考にしてください。','example_vi':'Hãy tham khảo nhé.'},
# 仕事 ===
  {'id':'仕事','reading':'しごと','meaning':'công việc, việc làm','kanji':['仕','事'],'jlpt':'N5','pitch':0,'example_jp':'仕事が忙しい。','example_vi':'Công việc bận rộn.'},
  {'id':'大事','reading':'だいじ','meaning':'quan trọng, đáng quý','kanji':['事'],'jlpt':'N4','pitch':0,'example_jp':'大事なものをなくした。','example_vi':'Tôi đánh mất thứ quan trọng.'},
  {'id':'行事','reading':'ぎょうじ','meaning':'sự kiện, lễ hội định kỳ','kanji':['事'],'jlpt':'N3','pitch':0,'example_jp':'学校行事に参加する。','example_vi':'Tham gia sự kiện của trường.'},
  {'id':'出来事','reading':'できごと','meaning':'sự việc đã xảy ra, sự cố','kanji':['事'],'jlpt':'N3','pitch':4,'example_jp':'面白い出来事があった。','example_vi':'Đã xảy ra việc thú vị.'},
# 所 ===
  {'id':'場所','reading':'ばしょ','meaning':'địa điểm, nơi chốn','kanji':['所'],'jlpt':'N4','pitch':0,'example_jp':'場所を教えてください。','example_vi':'Hãy cho tôi biết địa điểm.'},
  {'id':'台所','reading':'だいどころ','meaning':'nhà bếp','kanji':['所'],'jlpt':'N5','pitch':0,'example_jp':'台所で料理する。','example_vi':'Nấu ăn trong nhà bếp.'},
  {'id':'住所','reading':'じゅうしょ','meaning':'địa chỉ nhà','kanji':['所'],'jlpt':'N4','pitch':1,'example_jp':'住所を教えてください。','example_vi':'Hãy cho tôi biết địa chỉ.'},
  {'id':'近所','reading':'きんじょ','meaning':'hàng xóm, khu vực lân cận','kanji':['所'],'jlpt':'N4','pitch':1,'example_jp':'近所の人と仲良くする。','example_vi':'Thân thiện với hàng xóm.'},
# 家 ===
  {'id':'家族','reading':'かぞく','meaning':'gia đình','kanji':['家'],'jlpt':'N5','pitch':1,'example_jp':'家族と食事する。','example_vi':'Ăn cơm cùng gia đình.'},
  {'id':'家庭','reading':'かてい','meaning':'gia đình, hộ gia đình','kanji':['家'],'jlpt':'N4','pitch':0,'example_jp':'温かい家庭を築く。','example_vi':'Xây dựng gia đình ấm cúng.'},
  {'id':'家事','reading':'かじ','meaning':'việc nhà','kanji':['家'],'jlpt':'N4','pitch':1,'example_jp':'家事を分担する。','example_vi':'Chia sẻ công việc nhà.'},
  {'id':'専門家','reading':'せんもんか','meaning':'chuyên gia','kanji':['家'],'jlpt':'N3','pitch':4,'example_jp':'専門家に相談する。','example_vi':'Tham khảo ý kiến chuyên gia.'},
# 方 ===
  {'id':'方法','reading':'ほうほう','meaning':'phương pháp, cách thức','kanji':['方'],'jlpt':'N4','pitch':0,'example_jp':'効率的な方法を探す。','example_vi':'Tìm phương pháp hiệu quả.'},
  {'id':'一方','reading':'いっぽう','meaning':'một mặt, mặt khác; một chiều','kanji':['方','一'],'jlpt':'N3','pitch':0,'example_jp':'一方で問題もある。','example_vi':'Mặt khác cũng có vấn đề.'},
  {'id':'地方','reading':'ちほう','meaning':'địa phương, vùng nông thôn','kanji':['方'],'jlpt':'N3','pitch':0,'example_jp':'地方に引っ越した。','example_vi':'Tôi đã chuyển đến địa phương.'},
  {'id':'方向','reading':'ほうこう','meaning':'hướng đi, phương hướng','kanji':['方'],'jlpt':'N3','pitch':0,'example_jp':'方向を確認する。','example_vi':'Xác nhận hướng đi.'},
]

# Remove duplicates by id
seen = set()
unique_vocab = []
for v in vocab_data:
    if v['id'] not in seen:
        seen.add(v['id'])
        unique_vocab.append(v)

print(f'Total unique vocab entries: {len(unique_vocab)}')

# Write as JS
output = '// kanji-map-vocab-ext.js — extended vocab for kanji-map\n'
output += '// Auto-generated — do not edit manually\n\n'
output += 'var KANJI_MAP_VOCAB_EXT = [\n'
for v in unique_vocab:
    kanji_arr = ', '.join(f"'{k}'" for k in v['kanji'])
    # Escape single quotes in strings
    def esc(s): return s.replace("'", "\\'")
    output += f"  {{ id:'{esc(v['id'])}', reading:'{esc(v['reading'])}', meaning:'{esc(v['meaning'])}', kanji:[{kanji_arr}], jlpt:'{v['jlpt']}', pitch:{v.get('pitch',0)}, example_jp:'{esc(v.get('example_jp',''))}', example_vi:'{esc(v.get('example_vi',''))}' }},\n"
output += '];\n\n'
output += '''// Merge into KANJI_DATA.vocab when data is available
(function mergVocabExt() {
  function doMerge() {
    if (!window.KANJI_DATA || !window.KANJI_DATA.vocab) return false;
    var existingIds = new Set(window.KANJI_DATA.vocab.map(function(v){return v.id;}));
    var added = 0;
    KANJI_MAP_VOCAB_EXT.forEach(function(v) {
      if (!existingIds.has(v.id)) {
        window.KANJI_DATA.vocab.push(v);
        added++;
      }
    });
    console.log('[VocabExt] merged ' + added + ' entries, total: ' + window.KANJI_DATA.vocab.length);
    return true;
  }
  if (!doMerge()) {
    // KANJI_DATA not ready yet — retry after a tick
    var tries = 0;
    var t = setInterval(function() {
      tries++;
      if (doMerge() || tries > 20) clearInterval(t);
    }, 100);
  }
})();
'''

with open(r'C:\Users\hoang\Desktop\BUILD WEB KOERU\kanji-map-vocab-ext.js', 'w', encoding='utf-8') as f:
    f.write(output)
print('Written kanji-map-vocab-ext.js')
