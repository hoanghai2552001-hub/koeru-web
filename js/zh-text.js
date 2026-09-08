// KOERU — tiện ích xử lý chữ Hán / pinyin (đối xứng với js/jp-text.js)
// window.ZHText: esc, rubyfy, stripRuby, zhReading, plainPinyin, toneOf
(function(){
  // Bảng bỏ dấu thanh: dùng cho so khớp khi học sinh gõ pinyin không dấu.
  var TONE = {
    'ā':'a','á':'a','ǎ':'a','à':'a',
    'ē':'e','é':'e','ě':'e','è':'e',
    'ī':'i','í':'i','ǐ':'i','ì':'i',
    'ō':'o','ó':'o','ǒ':'o','ò':'o',
    'ū':'u','ú':'u','ǔ':'u','ù':'u',
    'ǖ':'v','ǘ':'v','ǚ':'v','ǜ':'v','ü':'v',
    'ń':'n','ň':'n','ǹ':'n','ɡ':'g'
  };
  // Thanh điệu của một âm tiết, suy từ dấu trên nguyên âm (0 = thanh nhẹ).
  var TONE_NUM = {
    'ā':1,'ē':1,'ī':1,'ō':1,'ū':1,'ǖ':1,
    'á':2,'é':2,'í':2,'ó':2,'ú':2,'ǘ':2,'ń':2,
    'ǎ':3,'ě':3,'ǐ':3,'ǒ':3,'ǔ':3,'ǚ':3,'ň':3,
    'à':4,'è':4,'ì':4,'ò':4,'ù':4,'ǜ':4,'ǹ':4
  };

  function esc(s){ var d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }

  // "汉[hàn]语[yǔ]" -> <ruby>汉<rt>hàn</rt></ruby><ruby>语<rt>yǔ</rt></ruby>
  function rubyfy(s){
    return esc(s).replace(/([一-鿿]+)\[([^\[\]]+)\]/g, '<ruby>$1<rt>$2</rt></ruby>');
  }
  function stripRuby(s){ return (s || '').replace(/\[[^\[\]]+\]/g, ''); }

  // Lấy phần pinyin ra khỏi chuỗi có ruby (dùng làm text cho TTS dự phòng)
  function zhReading(s){
    return (s || '').replace(/[一-鿿]+\[([^\[\]]+)\]/g, '$1').replace(/\[[^\[\]]+\]/g, '');
  }

  // Chuẩn hoá pinyin để so khớp: bỏ dấu thanh, bỏ khoảng trắng và dấu câu, thường hoá.
  // Nhờ vậy học sinh gõ "nihao" vẫn khớp với "nǐ hǎo".
  function plainPinyin(s){
    s = (s || '').toLowerCase().replace(/ɡ/g, 'g');
    var out = '';
    for(var i = 0; i < s.length; i++){
      var c = s[i];
      out += (TONE[c] !== undefined ? TONE[c] : c);
    }
    return out.replace(/[^a-z0-9]/g, '');
  }

  // Chuỗi số thanh điệu của cả từ: "nǐ hǎo" -> "3-3"
  function toneOf(s){
    var t = [];
    (s || '').split(/[\s·'’]+/).forEach(function(syl){
      if(!syl) return;
      var n = 0;
      for(var i = 0; i < syl.length; i++){
        if(TONE_NUM[syl[i]]){ n = TONE_NUM[syl[i]]; break; }
      }
      t.push(n);
    });
    return t.join('-');
  }

  window.ZHText = {
    esc: esc, rubyfy: rubyfy, stripRuby: stripRuby,
    zhReading: zhReading, plainPinyin: plainPinyin, toneOf: toneOf
  };
})();
