/* ════════════════════════════════
   KANA SPEED — Config
   Tách key/URL ra khỏi logic để dễ thay thế.
   Supabase anon key là public-safe (client-side),
   nhưng tách file giúp quản lý môi trường rõ hơn.
════════════════════════════════ */

const KANA_CONFIG = Object.freeze({
  supabaseUrl : 'https://vjcxtnynjpbebhosynkw.supabase.co',
  supabaseKey : 'sb_publishable_Hn4Dx5Gt7xuJkt35WRhU9w_aDaUwQHa',
  // Đổi thành false để tắt leaderboard (khi Supabase đổi project)
  leaderboardEnabled: true,
});
