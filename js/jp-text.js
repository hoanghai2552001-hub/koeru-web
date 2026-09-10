// Helper dùng chung: escape HTML + hiện furigana "漢字[かな]" -> <ruby>.
// Dùng bởi js/speak-practice.js và business.html (minna.html có bản riêng lâu đời hơn, không đụng vào).
(function(){
  function esc(s){ var d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }
  function rubyfy(s){ return esc(s).replace(/([一-鿿々]+)\[([ぁ-ゖー]+)\]/g,'<ruby>$1<rt>$2</rt></ruby>'); }
  function stripRuby(s){ return (s || '').replace(/\[[ぁ-ゖー]+\]/g,''); }
  function jpReading(s){ return (s || '').replace(/[一-鿿々]+\[([ぁ-ゖー]+)\]/g, '$1').replace(/\[[ぁ-ゖー]+\]/g,''); }
  window.JPText = { esc: esc, rubyfy: rubyfy, stripRuby: stripRuby, jpReading: jpReading };
})();
