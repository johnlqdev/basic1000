// Add silence before and after an MP3 clip without re-encoding it.
//
// Without a lead-in, the first word of a clip is often swallowed: many speakers and headphones
// only wake up once sound starts. So every clip gets a short silent start and end.
// The silence is made of "empty" MP3 frames copied from the clip's own frame header (same
// MPEG version, sample rate and channels) with all-zero side information, which every decoder
// plays as digital silence. The clip's ID3 tag and its Xing/Info header frame are dropped,
// because they describe the old length.

const BR1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320];
const BR2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160];
const SR: Record<number, number[]> = { 3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000] };

interface Frame { at: number; len: number; sr: number; spf: number; side: number; crc: boolean }

function frameAt(b: Uint8Array, i: number): Frame | null {
  if (i + 4 > b.length || b[i] !== 0xff || (b[i + 1] & 0xe0) !== 0xe0) return null;
  const ver = (b[i + 1] >> 3) & 3, layer = (b[i + 1] >> 1) & 3;
  const bri = b[i + 2] >> 4, sri = (b[i + 2] >> 2) & 3, pad = (b[i + 2] >> 1) & 1;
  if (ver === 1 || layer !== 1 || bri === 0 || bri === 15 || sri === 3) return null; // Layer III only
  const mpeg1 = ver === 3, mono = (b[i + 3] >> 6) === 3;
  const sr = SR[ver][sri], br = (mpeg1 ? BR1 : BR2)[bri] * 1000;
  const len = Math.floor(((mpeg1 ? 144 : 72) * br) / sr) + pad;
  const side = mpeg1 ? (mono ? 17 : 32) : (mono ? 9 : 17);
  return { at: i, len, sr, spf: mpeg1 ? 1152 : 576, side, crc: (b[i + 1] & 1) === 0 };
}

function tagAt(b: Uint8Array, i: number, s: string) {
  for (let k = 0; k < s.length; k++) if (b[i + k] !== s.charCodeAt(k)) return false;
  return true;
}

export function padMp3(src: Uint8Array, leadSec = 0.5, tailSec = 0.4): Uint8Array {
  let i = 0;
  if (tagAt(src, 0, "ID3") && src.length > 10) {
    const size = ((src[6] & 0x7f) << 21) | ((src[7] & 0x7f) << 14) | ((src[8] & 0x7f) << 7) | (src[9] & 0x7f);
    i = 10 + size + ((src[5] & 0x10) ? 10 : 0);
  }
  let end = src.length;
  if (end >= 128 && tagAt(src, end - 128, "TAG")) end -= 128;

  const frames: Frame[] = [];
  while (i < end) {
    const f = frameAt(src, i);
    // a real frame is followed by another frame (or the end); otherwise keep scanning for sync
    if (f && f.len > 4 && i + f.len <= end && (i + f.len === end || frameAt(src, i + f.len))) {
      frames.push(f); i += f.len;
    } else i++;
  }
  if (!frames.length) return src;

  const first = frames[0], off = first.at + 4 + (first.crc ? 2 : 0) + first.side;
  if (tagAt(src, off, "Xing") || tagAt(src, off, "Info") || tagAt(src, first.at + 36, "VBRI")) frames.shift();
  if (!frames.length) return src;

  // empty frame: the first audio frame's header without CRC or padding, then zeros
  const h = frames[0].at;
  const hdr = [src[h], src[h + 1] | 1, src[h + 2] & ~0x02, src[h + 3]];
  const silent = frameAt(new Uint8Array([...hdr, 0, 0, 0, 0]), 0)!;
  const blank = new Uint8Array(silent.len);
  blank.set(hdr);
  const nLead = Math.ceil((leadSec * silent.sr) / silent.spf), nTail = Math.ceil((tailSec * silent.sr) / silent.spf);

  const audioLen = frames.reduce((n, f) => n + f.len, 0);
  const out = new Uint8Array((nLead + nTail) * blank.length + audioLen);
  let o = 0;
  for (let k = 0; k < nLead; k++) { out.set(blank, o); o += blank.length; }
  for (const f of frames) { out.set(src.subarray(f.at, f.at + f.len), o); o += f.len; }
  for (let k = 0; k < nTail; k++) { out.set(blank, o); o += blank.length; }
  return out;
}
