import fontforge
import os

# מיפוי: שם אות → יוניקוד עברי
letter_map = {
    "alef": 0x05D0, "bet": 0x05D1, "gimel": 0x05D2, "dalet": 0x05D3,
    "he": 0x05D4, "vav": 0x05D5, "zayin": 0x05D6, "het": 0x05D7,
    "tet": 0x05D8, "yod": 0x05D9, "kaf": 0x05DB, "lamed": 0x05DC,
    "mem": 0x05DE, "nun": 0x05E0, "samekh": 0x05E1, "ayin": 0x05E2,
    "pe": 0x05E4, "tsadi": 0x05E6, "qof": 0x05E7, "resh": 0x05E8,
    "shin": 0x05E9, "tav": 0x05EA,
    "final_kaf": 0x05DA, "final_mem": 0x05DD, "final_nun": 0x05DF,
    "final_pe": 0x05E3, "final_tsadi": 0x05E5
}

def generate_ttf(svg_folder, output_ttf):
    try:
        font = fontforge.font()
        font.encoding = "UnicodeFull"
        font.fontname = "HebrewFont"
        font.familyname = "Hebrew Font"
        font.fullname = "Hebrew Font"
        font.em = 1000
        font.ascent = 800
        font.descent = 200

        glyph_count = 0

        for filename in os.listdir(svg_folder):
            if not filename.endswith(".svg"):
                continue

            parts = filename.split("_", 1)
            if len(parts) != 2:
                print(f"⚠️ שם לא תקני: {filename}")
                continue

            name = parts[1].replace(".svg", "")
            if name not in letter_map:
                print(f"⚠️ אות לא במפה: {name}")
                continue

            code = letter_map[name]
            svg_path = os.path.join(svg_folder, filename)

            g = font.createChar(code, name)
            try:
                g.importOutlines(svg_path)

                if g.boundingBox() == (0, 0, 0, 0):
                    print(f"⚠️ SVG ריק: {filename}")
                    continue

                xmin, ymin, xmax, ymax = g.boundingBox()
                g.width = int(xmax - xmin) + 80
                g.left_side_bearing = 27
                g.right_side_bearing = 27

                glyph_count += 1
                print(f"✅ {filename} → {name} ✓")

            except Exception as e:
                print(f"❌ שגיאה בקובץ {filename}: {e}")
                continue

        if glyph_count == 0:
            print("❌ לא נטען אף גליף – בדוק את קבצי ה־SVG")
            return False

        font.generate(output_ttf)
        print(f"✅ הפונט נוצר בהצלחה: {output_ttf}")
        return True

    except Exception as e:
        print(f"❌ שגיאה כללית ביצירת הפונט: {e}")
        return False
