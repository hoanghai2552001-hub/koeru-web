// ══════════════════════════════════════════
// KOERU — Hanzi Radical Explorer Data
// 20 bộ thủ phổ biến + chữ Hán HSK1–3
// ══════════════════════════════════════════

const HANZI_RADICAL_DATA = [
  {
    radical:"人", variant:"亻", pinyin:"rén", stroke:2,
    meaning_vi:"người", meaning_en:"person",
    characters:[
      {hanzi:"你",  pinyin:"nǐ",   meaning_vi:"bạn",             hsk:1},
      {hanzi:"他",  pinyin:"tā",   meaning_vi:"anh ấy",          hsk:1},
      {hanzi:"们",  pinyin:"men",  meaning_vi:"(số nhiều)",      hsk:1},
      {hanzi:"做",  pinyin:"zuò",  meaning_vi:"làm, thực hiện",  hsk:2},
      {hanzi:"住",  pinyin:"zhù",  meaning_vi:"ở, sống",         hsk:2},
      {hanzi:"从",  pinyin:"cóng", meaning_vi:"từ, theo",        hsk:2},
      {hanzi:"但",  pinyin:"dàn",  meaning_vi:"nhưng",           hsk:3},
      {hanzi:"信",  pinyin:"xìn",  meaning_vi:"thư, tin tưởng",  hsk:3},
    ]
  },
  {
    radical:"口", variant:"口", pinyin:"kǒu", stroke:3,
    meaning_vi:"miệng", meaning_en:"mouth",
    characters:[
      {hanzi:"吃",  pinyin:"chī",    meaning_vi:"ăn",            hsk:1},
      {hanzi:"喝",  pinyin:"hē",     meaning_vi:"uống",          hsk:1},
      {hanzi:"叫",  pinyin:"jiào",   meaning_vi:"gọi, kêu",      hsk:1},
      {hanzi:"问",  pinyin:"wèn",    meaning_vi:"hỏi",           hsk:1},
      {hanzi:"唱",  pinyin:"chàng",  meaning_vi:"hát",           hsk:2},
      {hanzi:"告",  pinyin:"gào",    meaning_vi:"báo, nói",      hsk:2},
      {hanzi:"哈",  pinyin:"hā",     meaning_vi:"ha (cười)",     hsk:0},
      {hanzi:"呢",  pinyin:"ne",     meaning_vi:"(trợ từ cuối)", hsk:1},
    ]
  },
  {
    radical:"手", variant:"扌", pinyin:"shǒu", stroke:4,
    meaning_vi:"tay", meaning_en:"hand",
    characters:[
      {hanzi:"打",  pinyin:"dǎ",   meaning_vi:"đánh, gọi điện", hsk:2},
      {hanzi:"找",  pinyin:"zhǎo", meaning_vi:"tìm",            hsk:2},
      {hanzi:"拿",  pinyin:"ná",   meaning_vi:"cầm, lấy",       hsk:3},
      {hanzi:"接",  pinyin:"jiē",  meaning_vi:"đón, tiếp nhận", hsk:3},
      {hanzi:"推",  pinyin:"tuī",  meaning_vi:"đẩy",            hsk:3},
      {hanzi:"报",  pinyin:"bào",  meaning_vi:"báo (giấy)",     hsk:2},
      {hanzi:"换",  pinyin:"huàn", meaning_vi:"đổi, thay",      hsk:3},
    ]
  },
  {
    radical:"水", variant:"氵", pinyin:"shuǐ", stroke:4,
    meaning_vi:"nước", meaning_en:"water",
    characters:[
      {hanzi:"洗",  pinyin:"xǐ",    meaning_vi:"rửa",            hsk:2},
      {hanzi:"游",  pinyin:"yóu",   meaning_vi:"bơi, du lịch",   hsk:2},
      {hanzi:"海",  pinyin:"hǎi",   meaning_vi:"biển",           hsk:3},
      {hanzi:"河",  pinyin:"hé",    meaning_vi:"sông",           hsk:3},
      {hanzi:"泳",  pinyin:"yǒng",  meaning_vi:"bơi lội",        hsk:2},
      {hanzi:"没",  pinyin:"méi",   meaning_vi:"không có",       hsk:1},
      {hanzi:"活",  pinyin:"huó",   meaning_vi:"sống",           hsk:3},
      {hanzi:"法",  pinyin:"fǎ",    meaning_vi:"pháp luật, cách",hsk:3},
    ]
  },
  {
    radical:"心", variant:"忄", pinyin:"xīn", stroke:4,
    meaning_vi:"tim, lòng", meaning_en:"heart/mind",
    characters:[
      {hanzi:"忙",  pinyin:"máng",   meaning_vi:"bận rộn",        hsk:2},
      {hanzi:"快",  pinyin:"kuài",   meaning_vi:"nhanh",          hsk:1},
      {hanzi:"想",  pinyin:"xiǎng",  meaning_vi:"nghĩ, nhớ",      hsk:1},
      {hanzi:"忘",  pinyin:"wàng",   meaning_vi:"quên",           hsk:3},
      {hanzi:"感",  pinyin:"gǎn",    meaning_vi:"cảm, xúc cảm",  hsk:3},
      {hanzi:"情",  pinyin:"qíng",   meaning_vi:"tình cảm",       hsk:3},
      {hanzi:"怕",  pinyin:"pà",     meaning_vi:"sợ",             hsk:2},
      {hanzi:"愉",  pinyin:"yú",     meaning_vi:"vui vẻ",         hsk:0},
    ]
  },
  {
    radical:"言", variant:"讠", pinyin:"yán", stroke:7,
    meaning_vi:"lời nói", meaning_en:"speech/words",
    characters:[
      {hanzi:"说",  pinyin:"shuō",  meaning_vi:"nói",            hsk:1},
      {hanzi:"话",  pinyin:"huà",   meaning_vi:"lời, câu chuyện",hsk:1},
      {hanzi:"请",  pinyin:"qǐng",  meaning_vi:"mời, xin",       hsk:1},
      {hanzi:"谢",  pinyin:"xiè",   meaning_vi:"cảm ơn",         hsk:1},
      {hanzi:"读",  pinyin:"dú",    meaning_vi:"đọc",            hsk:2},
      {hanzi:"认",  pinyin:"rèn",   meaning_vi:"nhận ra",        hsk:2},
      {hanzi:"语",  pinyin:"yǔ",    meaning_vi:"ngôn ngữ",       hsk:1},
      {hanzi:"词",  pinyin:"cí",    meaning_vi:"từ, bài hát",    hsk:3},
    ]
  },
  {
    radical:"木", variant:"木", pinyin:"mù", stroke:4,
    meaning_vi:"cây, gỗ", meaning_en:"wood/tree",
    characters:[
      {hanzi:"桌",  pinyin:"zhuō",  meaning_vi:"cái bàn",         hsk:2},
      {hanzi:"椅",  pinyin:"yǐ",    meaning_vi:"cái ghế",         hsk:2},
      {hanzi:"树",  pinyin:"shù",   meaning_vi:"cây (thực vật)",  hsk:3},
      {hanzi:"床",  pinyin:"chuáng",meaning_vi:"giường ngủ",      hsk:2},
      {hanzi:"杯",  pinyin:"bēi",   meaning_vi:"cốc, ly",         hsk:1},
      {hanzi:"本",  pinyin:"běn",   meaning_vi:"quyển, gốc",      hsk:2},
      {hanzi:"机",  pinyin:"jī",    meaning_vi:"máy móc",         hsk:2},
    ]
  },
  {
    radical:"日", variant:"日", pinyin:"rì", stroke:4,
    meaning_vi:"mặt trời, ngày", meaning_en:"sun/day",
    characters:[
      {hanzi:"明",  pinyin:"míng",  meaning_vi:"sáng, rõ ràng",  hsk:1},
      {hanzi:"时",  pinyin:"shí",   meaning_vi:"thời gian, lúc", hsk:2},
      {hanzi:"晚",  pinyin:"wǎn",   meaning_vi:"tối, muộn",      hsk:1},
      {hanzi:"早",  pinyin:"zǎo",   meaning_vi:"sáng, sớm",      hsk:1},
      {hanzi:"白",  pinyin:"bái",   meaning_vi:"trắng, ban ngày",hsk:1},
      {hanzi:"星",  pinyin:"xīng",  meaning_vi:"ngôi sao",       hsk:1},
      {hanzi:"暖",  pinyin:"nuǎn",  meaning_vi:"ấm áp",          hsk:3},
    ]
  },
  {
    radical:"女", variant:"女", pinyin:"nǚ", stroke:3,
    meaning_vi:"phụ nữ", meaning_en:"woman/female",
    characters:[
      {hanzi:"妈",  pinyin:"mā",   meaning_vi:"mẹ",              hsk:1},
      {hanzi:"她",  pinyin:"tā",   meaning_vi:"cô ấy",           hsk:1},
      {hanzi:"好",  pinyin:"hǎo",  meaning_vi:"tốt",             hsk:1},
      {hanzi:"姐",  pinyin:"jiě",  meaning_vi:"chị gái",         hsk:1},
      {hanzi:"妹",  pinyin:"mèi",  meaning_vi:"em gái",          hsk:1},
      {hanzi:"姓",  pinyin:"xìng", meaning_vi:"họ (tên họ)",     hsk:1},
      {hanzi:"奶",  pinyin:"nǎi",  meaning_vi:"bà nội, sữa",    hsk:1},
      {hanzi:"妻",  pinyin:"qī",   meaning_vi:"vợ",              hsk:3},
    ]
  },
  {
    radical:"土", variant:"土", pinyin:"tǔ", stroke:3,
    meaning_vi:"đất, đất đai", meaning_en:"earth/soil",
    characters:[
      {hanzi:"地",  pinyin:"dì",   meaning_vi:"đất, địa điểm",  hsk:1},
      {hanzi:"城",  pinyin:"chéng",meaning_vi:"thành phố",       hsk:2},
      {hanzi:"坐",  pinyin:"zuò",  meaning_vi:"ngồi",            hsk:1},
      {hanzi:"在",  pinyin:"zài",  meaning_vi:"ở, tại",          hsk:1},
      {hanzi:"坏",  pinyin:"huài", meaning_vi:"xấu, hỏng",       hsk:2},
      {hanzi:"场",  pinyin:"chǎng",meaning_vi:"sân, trường",     hsk:2},
      {hanzi:"块",  pinyin:"kuài", meaning_vi:"miếng, cục",      hsk:2},
    ]
  },
  {
    radical:"门", variant:"门", pinyin:"mén", stroke:3,
    meaning_vi:"cánh cửa", meaning_en:"door/gate",
    characters:[
      {hanzi:"门",  pinyin:"mén",  meaning_vi:"cửa",             hsk:1},
      {hanzi:"问",  pinyin:"wèn",  meaning_vi:"hỏi",             hsk:1},
      {hanzi:"开",  pinyin:"kāi",  meaning_vi:"mở",              hsk:1},
      {hanzi:"关",  pinyin:"guān", meaning_vi:"đóng, liên quan", hsk:2},
      {hanzi:"间",  pinyin:"jiān", meaning_vi:"phòng, khoảng",  hsk:2},
      {hanzi:"闻",  pinyin:"wén",  meaning_vi:"nghe, ngửi",      hsk:3},
    ]
  },
  {
    radical:"月", variant:"月", pinyin:"yuè", stroke:4,
    meaning_vi:"trăng, tháng", meaning_en:"moon/month",
    characters:[
      {hanzi:"月",  pinyin:"yuè",  meaning_vi:"tháng, trăng",   hsk:1},
      {hanzi:"朋",  pinyin:"péng", meaning_vi:"bạn bè",          hsk:1},
      {hanzi:"服",  pinyin:"fú",   meaning_vi:"quần áo, phục vụ",hsk:3},
      {hanzi:"期",  pinyin:"qī",   meaning_vi:"kỳ, giai đoạn",  hsk:2},
      {hanzi:"望",  pinyin:"wàng", meaning_vi:"trông mong",      hsk:2},
      {hanzi:"脸",  pinyin:"liǎn", meaning_vi:"khuôn mặt",       hsk:3},
    ]
  },
  {
    radical:"走", variant:"辶", pinyin:"zǒu", stroke:7,
    meaning_vi:"đi bộ, chạy", meaning_en:"walk/movement",
    characters:[
      {hanzi:"过",  pinyin:"guò",  meaning_vi:"qua, vượt qua",  hsk:2},
      {hanzi:"还",  pinyin:"hái",  meaning_vi:"còn, trở về",     hsk:1},
      {hanzi:"进",  pinyin:"jìn",  meaning_vi:"vào, tiến",       hsk:2},
      {hanzi:"边",  pinyin:"biān", meaning_vi:"bên, cạnh",       hsk:2},
      {hanzi:"近",  pinyin:"jìn",  meaning_vi:"gần",             hsk:2},
      {hanzi:"远",  pinyin:"yuǎn", meaning_vi:"xa",              hsk:2},
      {hanzi:"运",  pinyin:"yùn",  meaning_vi:"vận chuyển",      hsk:2},
      {hanzi:"道",  pinyin:"dào",  meaning_vi:"con đường, đạo",  hsk:3},
    ]
  },
  {
    radical:"火", variant:"灬", pinyin:"huǒ", stroke:4,
    meaning_vi:"lửa", meaning_en:"fire",
    characters:[
      {hanzi:"热",  pinyin:"rè",   meaning_vi:"nóng",            hsk:1},
      {hanzi:"然",  pinyin:"rán",  meaning_vi:"vậy, nhiên",      hsk:2},
      {hanzi:"熟",  pinyin:"shú",  meaning_vi:"chín, thuần thục",hsk:3},
      {hanzi:"炒",  pinyin:"chǎo", meaning_vi:"xào, rang",       hsk:3},
      {hanzi:"烤",  pinyin:"kǎo",  meaning_vi:"nướng",           hsk:3},
      {hanzi:"黑",  pinyin:"hēi",  meaning_vi:"đen",             hsk:2},
    ]
  },
  {
    radical:"金", variant:"钅", pinyin:"jīn", stroke:8,
    meaning_vi:"kim loại", meaning_en:"metal/gold",
    characters:[
      {hanzi:"钱",  pinyin:"qián", meaning_vi:"tiền",            hsk:1},
      {hanzi:"银",  pinyin:"yín",  meaning_vi:"bạc (kim loại)",  hsk:3},
      {hanzi:"铁",  pinyin:"tiě",  meaning_vi:"sắt",             hsk:2},
      {hanzi:"锻",  pinyin:"duàn", meaning_vi:"rèn luyện",       hsk:3},
      {hanzi:"针",  pinyin:"zhēn", meaning_vi:"kim, mũi kim",    hsk:3},
    ]
  },
  {
    radical:"食", variant:"饣", pinyin:"shí", stroke:9,
    meaning_vi:"ăn uống, đồ ăn", meaning_en:"food/eat",
    characters:[
      {hanzi:"饭",  pinyin:"fàn",  meaning_vi:"cơm, bữa ăn",    hsk:1},
      {hanzi:"饿",  pinyin:"è",    meaning_vi:"đói",             hsk:2},
      {hanzi:"饱",  pinyin:"bǎo",  meaning_vi:"no",              hsk:3},
      {hanzi:"饮",  pinyin:"yǐn",  meaning_vi:"đồ uống",         hsk:2},
      {hanzi:"馆",  pinyin:"guǎn", meaning_vi:"quán, nhà hàng",  hsk:2},
    ]
  },
  {
    radical:"目", variant:"目", pinyin:"mù", stroke:5,
    meaning_vi:"mắt", meaning_en:"eye",
    characters:[
      {hanzi:"看",  pinyin:"kàn",   meaning_vi:"xem, nhìn",      hsk:1},
      {hanzi:"眼",  pinyin:"yǎn",   meaning_vi:"mắt",            hsk:2},
      {hanzi:"睡",  pinyin:"shuì",  meaning_vi:"ngủ",            hsk:1},
      {hanzi:"睛",  pinyin:"jīng",  meaning_vi:"con ngươi (mắt)",hsk:2},
      {hanzi:"眉",  pinyin:"méi",   meaning_vi:"lông mày",       hsk:3},
    ]
  },
  {
    radical:"耳", variant:"耳", pinyin:"ěr", stroke:6,
    meaning_vi:"tai", meaning_en:"ear",
    characters:[
      {hanzi:"听",  pinyin:"tīng",  meaning_vi:"nghe",           hsk:1},
      {hanzi:"耳",  pinyin:"ěr",    meaning_vi:"tai",            hsk:1},
      {hanzi:"聪",  pinyin:"cōng",  meaning_vi:"thông minh",     hsk:3},
      {hanzi:"职",  pinyin:"zhí",   meaning_vi:"chức vụ",        hsk:3},
    ]
  },
  {
    radical:"艹", variant:"艹", pinyin:"cǎo", stroke:3,
    meaning_vi:"cỏ, thực vật", meaning_en:"grass/plant",
    characters:[
      {hanzi:"花",  pinyin:"huā",  meaning_vi:"hoa, chi tiêu",   hsk:2},
      {hanzi:"草",  pinyin:"cǎo",  meaning_vi:"cỏ",             hsk:2},
      {hanzi:"茶",  pinyin:"chá",  meaning_vi:"trà",             hsk:1},
      {hanzi:"英",  pinyin:"yīng", meaning_vi:"anh (nước Anh)",  hsk:1},
      {hanzi:"菜",  pinyin:"cài",  meaning_vi:"rau, món ăn",     hsk:1},
      {hanzi:"药",  pinyin:"yào",  meaning_vi:"thuốc",           hsk:2},
      {hanzi:"蓝",  pinyin:"lán",  meaning_vi:"màu xanh lam",   hsk:2},
    ]
  },
  {
    radical:"大", variant:"大", pinyin:"dà", stroke:3,
    meaning_vi:"to lớn", meaning_en:"big/great",
    characters:[
      {hanzi:"大",  pinyin:"dà",   meaning_vi:"to, lớn",         hsk:1},
      {hanzi:"太",  pinyin:"tài",  meaning_vi:"quá, rất",        hsk:1},
      {hanzi:"天",  pinyin:"tiān", meaning_vi:"trời, ngày",      hsk:1},
      {hanzi:"夫",  pinyin:"fū",   meaning_vi:"ông, chồng",      hsk:2},
      {hanzi:"美",  pinyin:"měi",  meaning_vi:"đẹp, nước Mỹ",   hsk:2},
      {hanzi:"奖",  pinyin:"jiǎng",meaning_vi:"giải thưởng",     hsk:3},
    ]
  },
];
