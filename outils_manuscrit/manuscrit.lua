-- manuscrit.lua -- irregularites d'ecriture a la main pour LuaLaTeX
-- (1) avant la coupure des lignes : espacement aleatoire entre lettres et entre mots ;
-- (2) a l'expedition de chaque page : chaque glyphe (texte ET maths) recoit une petite
--     transformation (rotation, echelle, inclinaison, decalage), coherente par mot
--     + bruit propre a chaque lettre. Rien n'est identique d'une lettre a l'autre.
manuscrit = manuscrit or {}
local M = manuscrit
-- polices considerees comme "manuscrites" (les autres -- maths -- recoivent en plus
-- l'inclinaison de l'ecriture) : motifs cherches dans le nom de la police
M.handfonts = M.handfonts or { "Kalam", "Patrick" }

local GLYPH, KERN, GLUE = node.id("glyph"), node.id("kern"), node.id("glue")
local HLIST, VLIST, DISC, MATH = node.id("hlist"), node.id("vlist"), node.id("disc"), node.id("math")
local insert_before, insert_after = node.insert_before, node.insert_after
local PT = 65536

M.params = {
  letter = 0.022,    -- ecart-type de l'espace entre deux lettres (em)
  letter_min = -0.03, letter_max = 0.06, -- bornes (pas de collisions)
  wordspace = 0.018, -- lettres d'un meme mot un peu plus serrees/espacees (em)
  math_slant = 0.12, -- les maths (Euler, symboles) penchent comme l'ecriture
  space = 0.17,      -- variation relative des espaces entre mots
  mathspace = 0.18,  -- variation relative des espaces en mode math
  rot_word = 1.1, rot_glyph = 1.7,      -- rotations (degres)
  sx_word = 0.025, sx_glyph = 0.032,    -- largeur
  sy_word = 0.030, sy_glyph = 0.038,    -- hauteur
  sh_word = 0.035, sh_glyph = 0.045,    -- inclinaison (cisaillement)
  dy_word = 0.15, dy_glyph = 0.11,      -- ligne de base (pt)
  dx_glyph = 0.06,                      -- decalage horizontal (pt)
}

math.randomseed(20261102)
local random, sqrt, log, cos, sin, pi, floor = math.random, math.sqrt, math.log, math.cos, math.sin, math.pi, math.floor
local function gauss()
  local u = random(); if u < 1e-12 then u = 1e-12 end
  return sqrt(-2 * log(u)) * cos(2 * pi * random())
end
local function clamp(x, a, b) if x < a then return a elseif x > b then return b end return x end

local fontsize, handfont = {}, {}
local function is_hand(f)   -- police manuscrite ?
  local h = handfont[f]
  if h == nil then
    local fnt = font.getfont(f)
    local nm = fnt and ((fnt.fullname or "") .. " " .. (fnt.name or "") .. " " .. (fnt.psname or "")) or ""
    h = false
    for _, pat in ipairs(M.handfonts) do
      if nm:find(pat, 1, true) then h = true end
    end
    handfont[f] = h
  end
  return h
end
local function em(f)
  local s = fontsize[f]
  if not s then
    local fnt = font.getfont(f)
    s = (fnt and fnt.size) or 10 * PT
    fontsize[f] = s
  end
  return s
end

---------------------------------------------------------------- (1) espacement
local function next_glyph(n)
  local m = n.next
  while m and m.id == KERN and m.subtype == 0 do m = m.next end
  if m and m.id == GLYPH then return m end
  return nil
end

function M.spacing(head)
  local P = M.params
  local inmath = false
  local wshift = gauss() * P.wordspace
  local n = head
  while n do
    local id = n.id
    if id == MATH then
      inmath = (n.subtype == 0)
    elseif id == GLUE then
      local st = n.subtype
      if not inmath and (st == 0 or st == 13 or st == 14) then
        n.width = floor(n.width * clamp(1 + gauss() * P.space, 0.6, 1.6))
        wshift = gauss() * P.wordspace
      elseif inmath and n.width > 0 then
        n.width = floor(n.width * clamp(1 + gauss() * P.mathspace, 0.55, 1.6))
      end
    elseif id == GLYPH then
      if next_glyph(n) then
        local amount = inmath and gauss() * P.letter * 0.6 or (gauss() * P.letter + wshift)
        amount = clamp(amount, P.letter_min, P.letter_max)
        local k = node.new(KERN, 1)
        k.kern = floor(amount * em(n.font))
        head, n = insert_after(head, n, k)
      end
    end
    n = n.next
  end
  return head
end

---------------------------------------------------------------- (2) glyphes
local function new_matrix(a, b, c, d)
  local w = node.new("whatsit", "pdf_setmatrix")
  w.data = string.format("%.5f %.5f %.5f %.5f", a, b, c, d)
  return w
end
local function new_kern(w) local k = node.new(KERN, 1); k.kern = w; return k end

local function word_state()
  local P = M.params
  return { rot = gauss() * P.rot_word, sx = 1 + gauss() * P.sx_word, sy = 1 + gauss() * P.sy_word,
           sh = gauss() * P.sh_word, dy = gauss() * P.dy_word * PT }
end

local function transform(head, g, ws)
  local P = M.params
  local th = clamp(ws.rot + gauss() * P.rot_glyph, -5, 5) * pi / 180
  local sx = clamp(ws.sx * (1 + gauss() * P.sx_glyph), 0.88, 1.12)
  local sy = clamp(ws.sy * (1 + gauss() * P.sy_glyph), 0.88, 1.12)
  local k  = clamp(ws.sh + gauss() * P.sh_glyph, -0.15, 0.15)
  if not is_hand(g.font) then k = k + P.math_slant end
  local c, s = cos(th), sin(th)
  -- R(th) * [[sx, k], [0, sy]] ; convention PDF : x' = a x + c y, y' = b x + d y
  local a, b, cc, d = c * sx, s * sx, c * k - s * sy, s * k + c * sy
  g.yoffset = (g.yoffset or 0) + floor(ws.dy + gauss() * P.dy_glyph * PT)
  g.xoffset = (g.xoffset or 0) + floor(gauss() * P.dx_glyph * PT)
  local w = g.width
  -- save, matrice (autour du point courant), glyphe, kern -w, restore, kern +w :
  -- la position est la meme au save et au restore (sinon "Misplaced \pdfrestore").
  head = insert_before(head, g, node.new("whatsit", "pdf_save"))
  head = insert_before(head, g, new_matrix(a, b, cc, d))
  local k1, r, k2
  head, k1 = insert_after(head, g, new_kern(-w))
  head, r  = insert_after(head, k1, node.new("whatsit", "pdf_restore"))
  head, k2 = insert_after(head, r, new_kern(w))
  return head, k2
end

local walk
walk = function(head, ws, vertical)
  local n = head
  if not vertical then ws = ws or word_state() end
  while n do
    local id = n.id
    if id == GLYPH then
      head, n = transform(head, n, ws)
    elseif id == HLIST then
      if n.head then n.head = walk(n.head, (not vertical) and ws or nil, false) end
    elseif id == VLIST then
      if n.head then n.head = walk(n.head, nil, true) end
    elseif id == GLUE then
      if not vertical then ws = word_state() end
    elseif id == DISC then
      if n.replace then n.replace = walk(n.replace, ws, false) end
    end
    n = n.next
  end
  return head
end

function M.page(boxnum)
  local b = tex.getbox(boxnum)
  if b and b.head then b.head = walk(b.head, nil, b.id == VLIST) end
end

function M.enable()
  luatexbase.add_to_callback("pre_linebreak_filter", M.spacing, "manuscrit.spacing")
end

return M
