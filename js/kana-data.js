/* ════════════════════════════════
   KANA SPEED — Data
   Hiragana · Katakana · Vocabulary MNN1
════════════════════════════════ */

const HIRAGANA_BASIC = [
  {k:'あ',r:'a'},{k:'い',r:'i'},{k:'う',r:'u'},{k:'え',r:'e'},{k:'お',r:'o'},
  {k:'か',r:'ka'},{k:'き',r:'ki'},{k:'く',r:'ku'},{k:'け',r:'ke'},{k:'こ',r:'ko'},
  {k:'さ',r:'sa'},{k:'し',r:'shi'},{k:'す',r:'su'},{k:'せ',r:'se'},{k:'そ',r:'so'},
  {k:'た',r:'ta'},{k:'ち',r:'chi'},{k:'つ',r:'tsu'},{k:'て',r:'te'},{k:'と',r:'to'},
  {k:'な',r:'na'},{k:'に',r:'ni'},{k:'ぬ',r:'nu'},{k:'ね',r:'ne'},{k:'の',r:'no'},
  {k:'は',r:'ha'},{k:'ひ',r:'hi'},{k:'ふ',r:'fu'},{k:'へ',r:'he'},{k:'ほ',r:'ho'},
  {k:'ま',r:'ma'},{k:'み',r:'mi'},{k:'む',r:'mu'},{k:'め',r:'me'},{k:'も',r:'mo'},
  {k:'や',r:'ya'},{k:'ゆ',r:'yu'},{k:'よ',r:'yo'},
  {k:'ら',r:'ra'},{k:'り',r:'ri'},{k:'る',r:'ru'},{k:'れ',r:'re'},{k:'ろ',r:'ro'},
  {k:'わ',r:'wa'},{k:'を',r:'wo'},{k:'ん',r:'n'},
];

const HIRAGANA_ADVANCED = [
  // Âm đục (dakuten)
  {k:'が',r:'ga'},{k:'ぎ',r:'gi'},{k:'ぐ',r:'gu'},{k:'げ',r:'ge'},{k:'ご',r:'go'},
  {k:'ざ',r:'za'},{k:'じ',r:'ji'},{k:'ず',r:'zu'},{k:'ぜ',r:'ze'},{k:'ぞ',r:'zo'},
  {k:'だ',r:'da'},{k:'ぢ',r:'ji'},{k:'づ',r:'zu'},{k:'で',r:'de'},{k:'ど',r:'do'},
  {k:'ば',r:'ba'},{k:'び',r:'bi'},{k:'ぶ',r:'bu'},{k:'べ',r:'be'},{k:'ぼ',r:'bo'},
  // Âm bán đục (handakuten)
  {k:'ぱ',r:'pa'},{k:'ぴ',r:'pi'},{k:'ぷ',r:'pu'},{k:'ぺ',r:'pe'},{k:'ぽ',r:'po'},
  // Âm ghép (youon)
  {k:'きゃ',r:'kya'},{k:'きゅ',r:'kyu'},{k:'きょ',r:'kyo'},
  {k:'しゃ',r:'sha'},{k:'しゅ',r:'shu'},{k:'しょ',r:'sho'},
  {k:'ちゃ',r:'cha'},{k:'ちゅ',r:'chu'},{k:'ちょ',r:'cho'},
  {k:'にゃ',r:'nya'},{k:'にゅ',r:'nyu'},{k:'にょ',r:'nyo'},
  {k:'ひゃ',r:'hya'},{k:'ひゅ',r:'hyu'},{k:'ひょ',r:'hyo'},
  {k:'みゃ',r:'mya'},{k:'みゅ',r:'myu'},{k:'みょ',r:'myo'},
  {k:'りゃ',r:'rya'},{k:'りゅ',r:'ryu'},{k:'りょ',r:'ryo'},
  {k:'ぎゃ',r:'gya'},{k:'ぎゅ',r:'gyu'},{k:'ぎょ',r:'gyo'},
  {k:'じゃ',r:'ja'},{k:'じゅ',r:'ju'},{k:'じょ',r:'jo'},
  {k:'びゃ',r:'bya'},{k:'びゅ',r:'byu'},{k:'びょ',r:'byo'},
  {k:'ぴゃ',r:'pya'},{k:'ぴゅ',r:'pyu'},{k:'ぴょ',r:'pyo'},
  {k:'っ',r:'(tsu nhỏ)'},
];

const KATAKANA_BASIC = [
  {k:'ア',r:'a'},{k:'イ',r:'i'},{k:'ウ',r:'u'},{k:'エ',r:'e'},{k:'オ',r:'o'},
  {k:'カ',r:'ka'},{k:'キ',r:'ki'},{k:'ク',r:'ku'},{k:'ケ',r:'ke'},{k:'コ',r:'ko'},
  {k:'サ',r:'sa'},{k:'シ',r:'shi'},{k:'ス',r:'su'},{k:'セ',r:'se'},{k:'ソ',r:'so'},
  {k:'タ',r:'ta'},{k:'チ',r:'chi'},{k:'ツ',r:'tsu'},{k:'テ',r:'te'},{k:'ト',r:'to'},
  {k:'ナ',r:'na'},{k:'ニ',r:'ni'},{k:'ヌ',r:'nu'},{k:'ネ',r:'ne'},{k:'ノ',r:'no'},
  {k:'ハ',r:'ha'},{k:'ヒ',r:'hi'},{k:'フ',r:'fu'},{k:'ヘ',r:'he'},{k:'ホ',r:'ho'},
  {k:'マ',r:'ma'},{k:'ミ',r:'mi'},{k:'ム',r:'mu'},{k:'メ',r:'me'},{k:'モ',r:'mo'},
  {k:'ヤ',r:'ya'},{k:'ユ',r:'yu'},{k:'ヨ',r:'yo'},
  {k:'ラ',r:'ra'},{k:'リ',r:'ri'},{k:'ル',r:'ru'},{k:'レ',r:'re'},{k:'ロ',r:'ro'},
  {k:'ワ',r:'wa'},{k:'ヲ',r:'wo'},{k:'ン',r:'n'},
];

const KATAKANA_ADVANCED = [
  {k:'ガ',r:'ga'},{k:'ギ',r:'gi'},{k:'グ',r:'gu'},{k:'ゲ',r:'ge'},{k:'ゴ',r:'go'},
  {k:'ザ',r:'za'},{k:'ジ',r:'ji'},{k:'ズ',r:'zu'},{k:'ゼ',r:'ze'},{k:'ゾ',r:'zo'},
  {k:'ダ',r:'da'},{k:'ヂ',r:'ji'},{k:'ヅ',r:'zu'},{k:'デ',r:'de'},{k:'ド',r:'do'},
  {k:'バ',r:'ba'},{k:'ビ',r:'bi'},{k:'ブ',r:'bu'},{k:'ベ',r:'be'},{k:'ボ',r:'bo'},
  {k:'パ',r:'pa'},{k:'ピ',r:'pi'},{k:'プ',r:'pu'},{k:'ペ',r:'pe'},{k:'ポ',r:'po'},
  {k:'キャ',r:'kya'},{k:'キュ',r:'kyu'},{k:'キョ',r:'kyo'},
  {k:'シャ',r:'sha'},{k:'シュ',r:'shu'},{k:'ショ',r:'sho'},
  {k:'チャ',r:'cha'},{k:'チュ',r:'chu'},{k:'チョ',r:'cho'},
  {k:'ニャ',r:'nya'},{k:'ニュ',r:'nyu'},{k:'ニョ',r:'nyo'},
  {k:'ヒャ',r:'hya'},{k:'ヒュ',r:'hyu'},{k:'ヒョ',r:'hyo'},
  {k:'ミャ',r:'mya'},{k:'ミュ',r:'myu'},{k:'ミョ',r:'myo'},
  {k:'リャ',r:'rya'},{k:'リュ',r:'ryu'},{k:'リョ',r:'ryo'},
  {k:'ギャ',r:'gya'},{k:'ギュ',r:'gyu'},{k:'ギョ',r:'gyo'},
  {k:'ジャ',r:'ja'},{k:'ジュ',r:'ju'},{k:'ジョ',r:'jo'},
  {k:'ビャ',r:'bya'},{k:'ビュ',r:'byu'},{k:'ビョ',r:'byo'},
  {k:'ピャ',r:'pya'},{k:'ピュ',r:'pyu'},{k:'ピョ',r:'pyo'},
  {k:'ー',r:'(trường âm)'},
  {k:'ッ',r:'(tsu nhỏ)'},
];

// ─── LEVEL 3: Từ vựng Minna no Nihongo 1 ───
const VOCAB_MNN1 = [
  // Bài 1 — Người, nghề nghiệp
  {k:'がくせい',r:'gakusei',m:'học sinh/sinh viên'},
  {k:'せんせい',r:'sensei',m:'giáo viên'},
  {k:'かいしゃいん',r:'kaishain',m:'nhân viên công ty'},
  {k:'いしゃ',r:'isha',m:'bác sĩ'},
  {k:'けんきゅうしゃ',r:'kenkyuusha',m:'nhà nghiên cứu'},
  {k:'エンジニア',r:'enjinia',m:'kỹ sư'},
  // Bài 2 — Đồ vật
  {k:'これ',r:'kore',m:'cái này'},{k:'それ',r:'sore',m:'cái đó'},{k:'あれ',r:'are',m:'cái kia'},
  {k:'ほん',r:'hon',m:'sách'},{k:'ざっし',r:'zasshi',m:'tạp chí'},{k:'しんぶん',r:'shinbun',m:'báo'},
  {k:'ノート',r:'nooto',m:'vở/notebook'},{k:'テキスト',r:'tekisuto',m:'giáo trình'},
  {k:'えんぴつ',r:'enpitsu',m:'bút chì'},{k:'かぎ',r:'kagi',m:'chìa khóa'},
  {k:'とけい',r:'tokei',m:'đồng hồ'},{k:'かさ',r:'kasa',m:'ô/dù'},
  {k:'かばん',r:'kaban',m:'túi/cặp'},{k:'くるま',r:'kuruma',m:'xe hơi'},
  // Bài 3 — Nơi chốn
  {k:'ここ',r:'koko',m:'ở đây'},{k:'そこ',r:'soko',m:'ở đó'},{k:'あそこ',r:'asoko',m:'ở kia'},
  {k:'トイレ',r:'toire',m:'nhà vệ sinh'},{k:'エレベーター',r:'erebeetaa',m:'thang máy'},{k:'かいだん',r:'kaidan',m:'cầu thang'},
  // Bài 4 — Thời gian
  {k:'いま',r:'ima',m:'bây giờ'},{k:'なんじ',r:'nanji',m:'mấy giờ'},
  {k:'ごぜん',r:'gozen',m:'buổi sáng (AM)'},{k:'ごご',r:'gogo',m:'buổi chiều (PM)'},{k:'はん',r:'han',m:'rưỡi'},
  // Bài 5 — Mua sắm
  {k:'いくら',r:'ikura',m:'bao nhiêu tiền'},{k:'みせ',r:'mise',m:'cửa hàng'},
  {k:'デパート',r:'depaato',m:'trung tâm thương mại'},{k:'やおや',r:'yaoya',m:'cửa hàng rau củ'},
  {k:'にく',r:'niku',m:'thịt'},{k:'さかな',r:'sakana',m:'cá'},{k:'やさい',r:'yasai',m:'rau'},
  {k:'くだもの',r:'kudamono',m:'hoa quả'},{k:'たまご',r:'tamago',m:'trứng'},{k:'パン',r:'pan',m:'bánh mì'},
  // Bài 6 — Ăn uống
  {k:'たべます',r:'tabemasu',m:'ăn'},{k:'のみます',r:'nomimasu',m:'uống'},
  {k:'みず',r:'mizu',m:'nước'},{k:'おちゃ',r:'ocha',m:'trà'},
  {k:'コーヒー',r:'koohii',m:'cà phê'},{k:'ビール',r:'biiru',m:'bia'},
  {k:'あさごはん',r:'asagohan',m:'bữa sáng'},{k:'ひるごはん',r:'hirugohan',m:'bữa trưa'},{k:'ばんごはん',r:'bangohan',m:'bữa tối'},
  // Bài 7 — Hành động
  {k:'みます',r:'mimasu',m:'xem'},{k:'ききます',r:'kikimasu',m:'nghe'},
  {k:'よみます',r:'yomimasu',m:'đọc'},{k:'かきます',r:'kakimasu',m:'viết'},
  {k:'かいます',r:'kaimasu',m:'mua'},{k:'します',r:'shimasu',m:'làm'},
  // Bài 8 — Địa điểm & giao thông
  {k:'えき',r:'eki',m:'ga tàu'},{k:'くうこう',r:'kuukou',m:'sân bay'},
  {k:'びょういん',r:'byouin',m:'bệnh viện'},{k:'ぎんこう',r:'ginkou',m:'ngân hàng'},{k:'ゆうびんきょく',r:'yuubinkyoku',m:'bưu điện'},
  {k:'でんしゃ',r:'densha',m:'tàu điện'},{k:'バス',r:'basu',m:'xe buýt'},{k:'タクシー',r:'takushii',m:'taxi'},{k:'ひこうき',r:'hikouki',m:'máy bay'},
  // Bài 9-10 — Thời gian & tần suất
  {k:'きょう',r:'kyou',m:'hôm nay'},{k:'きのう',r:'kinou',m:'hôm qua'},{k:'あした',r:'ashita',m:'ngày mai'},
  {k:'まいにち',r:'mainichi',m:'mỗi ngày'},{k:'やすみ',r:'yasumi',m:'ngày nghỉ'},{k:'しごと',r:'shigoto',m:'công việc'},
  {k:'がっこう',r:'gakkou',m:'trường học'},{k:'せんしゅう',r:'senshuu',m:'tuần trước'},{k:'らいしゅう',r:'raishuu',m:'tuần sau'},{k:'れんしゅう',r:'renshuu',m:'luyện tập'},
  // Bài 11-12 — Động từ
  {k:'はなします',r:'hanashimasu',m:'nói/kể'},{k:'わかります',r:'wakarimasu',m:'hiểu'},
  {k:'あります',r:'arimasu',m:'có (vật)'},{k:'います',r:'imasu',m:'có (người/động vật)'},
  {k:'おきます',r:'okimasu',m:'thức dậy'},{k:'ねます',r:'nemasu',m:'đi ngủ'},
  {k:'はたらきます',r:'hatarakimasu',m:'làm việc'},{k:'やすみます',r:'yasumimasu',m:'nghỉ ngơi'},
  {k:'べんきょうします',r:'benkyoushimasu',m:'học bài'},{k:'さんぽします',r:'sanposhimasu',m:'đi dạo'},
  // Bài 13-14 — Tính từ -い
  {k:'おおきい',r:'ookii',m:'to/lớn'},{k:'ちいさい',r:'chiisai',m:'nhỏ/bé'},
  {k:'あたらしい',r:'atarashii',m:'mới'},{k:'ふるい',r:'furui',m:'cũ'},
  {k:'たかい',r:'takai',m:'cao/đắt'},{k:'やすい',r:'yasui',m:'rẻ'},
  {k:'はやい',r:'hayai',m:'nhanh/sớm'},{k:'おそい',r:'osoi',m:'chậm/muộn'},
  {k:'あつい',r:'atsui',m:'nóng'},{k:'さむい',r:'samui',m:'lạnh'},
  {k:'むずかしい',r:'muzukashii',m:'khó'},{k:'やさしい',r:'yasashii',m:'dễ/hiền'},
  {k:'おもしろい',r:'omoshiroi',m:'thú vị'},{k:'つまらない',r:'tsumaranai',m:'nhàm chán'},{k:'いそがしい',r:'isogashii',m:'bận rộn'},
  // Bài 15 — Tính từ -な
  {k:'きれい',r:'kirei',m:'đẹp/sạch'},{k:'しずか',r:'shizuka',m:'yên tĩnh'},
  {k:'にぎやか',r:'nigiyaka',m:'nhộn nhịp'},{k:'ゆうめい',r:'yuumei',m:'nổi tiếng'},
  {k:'べんり',r:'benri',m:'tiện lợi'},{k:'すき',r:'suki',m:'thích'},
  {k:'きらい',r:'kirai',m:'ghét'},{k:'じょうず',r:'jouzu',m:'giỏi'},{k:'へた',r:'heta',m:'kém/vụng'},
  // Bài 16-17 — Gia đình
  {k:'かぞく',r:'kazoku',m:'gia đình'},{k:'おとうさん',r:'otousan',m:'bố'},{k:'おかあさん',r:'okaasan',m:'mẹ'},
  {k:'おにいさん',r:'oniisan',m:'anh trai'},{k:'おねえさん',r:'oneesan',m:'chị gái'},
  {k:'おとうと',r:'otouto',m:'em trai'},{k:'いもうと',r:'imouto',m:'em gái'},
  {k:'こども',r:'kodomo',m:'trẻ em/con'},{k:'ともだち',r:'tomodachi',m:'bạn bè'},
  // Bài 18-19 — Sở thích
  {k:'スポーツ',r:'supootsu',m:'thể thao'},{k:'サッカー',r:'sakkaa',m:'bóng đá'},{k:'テニス',r:'tenisu',m:'tennis'},
  {k:'おんがく',r:'ongaku',m:'âm nhạc'},{k:'えいが',r:'eiga',m:'phim'},{k:'りょこう',r:'ryokou',m:'du lịch'},{k:'りょうり',r:'ryouri',m:'nấu ăn'},
  // Bài 20-21 — Thời tiết
  {k:'てんき',r:'tenki',m:'thời tiết'},{k:'あめ',r:'ame',m:'mưa'},{k:'ゆき',r:'yuki',m:'tuyết'},
  {k:'かぜ',r:'kaze',m:'gió'},{k:'はる',r:'haru',m:'mùa xuân'},{k:'なつ',r:'natsu',m:'mùa hè'},{k:'あき',r:'aki',m:'mùa thu'},{k:'ふゆ',r:'fuyu',m:'mùa đông'},
  // Bài 22-25 — Màu sắc & hướng
  {k:'いろ',r:'iro',m:'màu sắc'},{k:'しろ',r:'shiro',m:'trắng'},{k:'くろ',r:'kuro',m:'đen'},
  {k:'あか',r:'aka',m:'đỏ'},{k:'あお',r:'ao',m:'xanh'},{k:'きいろ',r:'kiiro',m:'vàng'},
  {k:'みぎ',r:'migi',m:'bên phải'},{k:'ひだり',r:'hidari',m:'bên trái'},{k:'まっすぐ',r:'massugu',m:'đi thẳng'},
  {k:'となり',r:'tonari',m:'bên cạnh'},{k:'まえ',r:'mae',m:'phía trước'},{k:'うしろ',r:'ushiro',m:'phía sau'},
  {k:'うえ',r:'ue',m:'phía trên'},{k:'した',r:'shita',m:'phía dưới'},{k:'なか',r:'naka',m:'bên trong'},
];
