# نتائج الفحص الفعلي للمفاتيح — 27 أكتوبر 2026

وقت التقرير UTC: `2026-10-27T17:53:54.242978+00:00`
[تشغيل GitHub الناجح](https://github.com/bitdogemostafa2-sys/youtube-programmer/actions/runs/40554701561)

## الخلاصة المؤكدة

- استلم الفاحص 28 مدخلًا، بترقيم مستقل لكل مزوّد حسب ترتيب المستخدم.
- نجحت طلبات القراءة لـ19 مدخلًا. أعادت 7 مفاتيح Groq حالة HTTP 400؛ السبب التفصيلي غير محسوم.
- مدخلا Cloudflare لم يصلا إلى الشبكة لأن المحوّل لا يدعم صيغة معرف الحساب:البريد:المفتاح المرسلة. هذا ليس حكمًا على صلاحية المفتاح.
- لم تُرسل طلبات توليد نصوص أو صور أو فيديو أو صوت أو مؤثرات. لا نموذج معتمد للإدماج باعتباره مجانيًا ومختبر التوليد بعد.
- تم التحقق من اكتمال التقرير بواسطة gzip CRC وبصمة SHA-256 قبل استخراج هذه النتائج.
- التشغيل السابق أعاد 18 نجاح قراءة؛ التقرير الحالي الكامل أعاد 19. النتيجة مرتبطة بوقت الطلب ولا تضمن الوصول الدائم.

## كل مفتاح على حدة

| معرّف المفتاح | النتيجة | عدد عناصر القائمة المعادة |
|---|---|---|
| GEMINI-01 | نجح طلب القراءة | 60 |
| GEMINI-02 | نجح طلب القراءة | 60 |
| GROQ-01 | نجح طلب القراءة | 11 |
| GROQ-02 | نجح طلب القراءة | 11 |
| GROQ-03 | أعاد المزوّد HTTP 400 | 0 |
| GROQ-04 | أعاد المزوّد HTTP 400 | 0 |
| GROQ-05 | أعاد المزوّد HTTP 400 | 0 |
| GROQ-06 | أعاد المزوّد HTTP 400 | 0 |
| GROQ-07 | أعاد المزوّد HTTP 400 | 0 |
| GROQ-08 | أعاد المزوّد HTTP 400 | 0 |
| GROQ-09 | أعاد المزوّد HTTP 400 | 0 |
| CLOUDFLARE-01 | لم يُرسل: صيغة Cloudflare غير مدعومة | 0 |
| CLOUDFLARE-02 | لم يُرسل: صيغة Cloudflare غير مدعومة | 0 |
| HUGGINGFACE-01 | نجح طلب القراءة | 0 |
| HUGGINGFACE-02 | نجح طلب القراءة | 0 |
| HUGGINGFACE-03 | نجح طلب القراءة | 0 |
| HUGGINGFACE-04 | نجح طلب القراءة | 0 |
| HUGGINGFACE-05 | نجح طلب القراءة | 0 |
| HUGGINGFACE-06 | نجح طلب القراءة | 0 |
| HUGGINGFACE-07 | نجح طلب القراءة | 0 |
| HUGGINGFACE-08 | نجح طلب القراءة | 0 |
| HUGGINGFACE-09 | نجح طلب القراءة | 0 |
| HUGGINGFACE-10 | نجح طلب القراءة | 0 |
| HUGGINGFACE-11 | نجح طلب القراءة | 0 |
| PEXELS-01 | نجح طلب القراءة | 1 |
| UNSPLASH-01 | نجح طلب القراءة | 1 |
| INWORLD-01 | نجح طلب القراءة | 300 |
| NASA-01 | نجح طلب القراءة | 1 |

## معنى النتائج لكل مزوّد

- **Gemini:** عاد 60 معرّف نموذج لكل مفتاح. هذه قائمة اكتشاف وليست إثبات إمكانية توليد كل نموذج أو مجانيته. لا نموذج فيديو مؤكد من هذا الفحص.
- **Groq:** عاد 11 معرّفًا لكل من GROQ-01 وGROQ-02. باقي المفاتيح أعادت 400، وليس 401؛ لا يصح الجزم بأنها ملغاة أو غير صالحة دون تشخيص إضافي.
- **Hugging Face:** نجح التحقق من الهوية للمفاتيح الأحد عشر. لم تُحفظ بيانات الهوية. هذا لا يحدد نماذج الاستدلال المجانية أو حصتها.
- **Pexels وUnsplash:** نجح بحث صور محدود لكل منهما. لم يُختبر بحث الفيديو أو تنزيل المواد، وهما مصدران لمواد جاهزة وليسَا مولدَي صور.
- **NASA:** نجح طلب APOD لتاريخ محدد، وليس اختبارًا لخدمات NASA كلها.
- **Cloudflare:** يجب دعم نوع المصادقة المرسل صراحة قبل اختباره، دون إسقاط البريد أو افتراض أن المفتاح Bearer token.

## المعلقون والأصوات

- **Inworld:** نجح طلب قائمة الأصوات وأعاد 300 معرّف صوت. لم تُولَّد تسجيلات بها. لا يثبت الرد أن كلها أصوات مخصصة مثبتة للحساب، ولا يضمن اكتمال أي صفحات إضافية.
- تتضمن القائمة: `Nour`، `Omar`، `Amina`، `Victor`، `Brian`، `Larissa`، `Jessica`، `Liam`. الاسم وحده ليس دليلًا على اللغة أو اللهجة أو الجودة.
- **Groq:** ظهر `canopylabs/orpheus-arabic-saudi` و`canopylabs/orpheus-v1-english` ضمن قائمة النماذج؛ لم تُختبر أصواتهما فعليًا ولم تُثبت المجانية.
- **Gemini:** ظهرت معرفات تتضمن TTS؛ هذه معرفات نماذج، وليست قائمة أصوات معلّقين مختبرة.
- قائمة Inworld الكاملة محفوظة محليًا في `.runtime/provider-audit/voices.csv` وفي التقرير المفصل.

## قوائم النماذج المعادة

التصنيف أدناه آلي واستدلالي من الاسم/المهمة، وليس إثبات قدرة. خصوصًا نماذج الحماية والتضمين ليست بديلًا مثبتًا لكتابة السكربتات، والنماذج متعددة الوسائط قد تُصنَّف تصنيفًا ناقصًا. جميعها: مجانية غير متحققة وتوليد غير مختبر.

### gemini — GEMINI-01, GEMINI-02

تطابقت مجموعات المعرفات بين المفاتيح الناجحة.

| المعرّف | التصنيف الآلي الأولي |
|---|---|
| `models/gemini-2.5-flash` | كتابة نصوص واسكربتات |
| `models/gemini-2.5-pro` | كتابة نصوص واسكربتات |
| `models/gemini-2.5-flash-preview-tts` | تعليق صوتي |
| `models/gemini-2.5-pro-preview-tts` | تعليق صوتي |
| `models/gemma-4-26b-a4b-it` | كتابة نصوص واسكربتات |
| `models/gemma-4-31b-it` | كتابة نصوص واسكربتات |
| `models/gemini-flash-latest` | كتابة نصوص واسكربتات |
| `models/gemini-flash-lite-latest` | كتابة نصوص واسكربتات |
| `models/gemini-pro-latest` | كتابة نصوص واسكربتات |
| `models/gemini-2.5-flash-lite` | كتابة نصوص واسكربتات |
| `models/gemini-2.5-flash-image` | توليد الصور |
| `models/gemini-3-flash-preview` | كتابة نصوص واسكربتات |
| `models/gemini-3.1-pro-preview` | كتابة نصوص واسكربتات |
| `models/gemini-3.1-pro-preview-customtools` | كتابة نصوص واسكربتات |
| `models/gemini-3.1-flash-lite-preview` | كتابة نصوص واسكربتات |
| `models/gemini-3.1-flash-lite` | كتابة نصوص واسكربتات |
| `models/gemini-3-pro-image-preview` | توليد الصور |
| `models/gemini-3-pro-image` | توليد الصور |
| `models/nano-banana-pro-preview` | غير محسوم |
| `models/gemini-3.1-flash-image-preview` | توليد الصور |
| `models/gemini-3.1-flash-image` | توليد الصور |
| `models/gemini-3.1-flash-lite-image` | توليد الصور |
| `models/gemini-nano-banana-2.1` | كتابة نصوص واسكربتات |
| `models/gemini-3.5-flash` | كتابة نصوص واسكربتات |
| `models/gemini-3.5-flash-lite` | كتابة نصوص واسكربتات |
| `models/gemini-omni-flash-preview` | كتابة نصوص واسكربتات |
| `models/gemini-omni-1.1-flash` | كتابة نصوص واسكربتات |
| `models/gemini-3.5-transcribe` | كتابة نصوص واسكربتات |
| `models/gemini-3.6-flash` | كتابة نصوص واسكربتات |
| `models/gemini-3.7-flash` | كتابة نصوص واسكربتات |
| `models/gemini-3.8-flash` | كتابة نصوص واسكربتات |
| `models/gemini-4-argon` | كتابة نصوص واسكربتات |
| `models/lyria-3-clip-preview` | غير محسوم |
| `models/lyria-3-pro-preview` | غير محسوم |
| `models/lyria-3.5` | غير محسوم |
| `models/gemini-3.1-flash-tts-preview` | تعليق صوتي |
| `models/gemini-3.8-flash-tts` | تعليق صوتي |
| `models/gemini-3.8-flash-lite-tts` | تعليق صوتي |
| `models/gemini-robotics-er-2-preview` | كتابة نصوص واسكربتات |
| `models/gemini-2.5-computer-use-preview-10-2025` | كتابة نصوص واسكربتات |
| `models/antigravity-preview-05-2026` | غير محسوم |
| `models/antigravity-preview-09-2026` | غير محسوم |
| `models/antigravity-preview-latest` | غير محسوم |
| `models/deep-research-max-preview-04-2026` | غير محسوم |
| `models/deep-research-preview-04-2026` | غير محسوم |
| `models/deep-research-pro-preview-12-2025` | غير محسوم |
| `models/gemini-embedding-001` | تمثيل نصي للبحث؛ ليس توليد محتوى |
| `models/gemini-embedding-2-preview` | تمثيل نصي للبحث؛ ليس توليد محتوى |
| `models/gemini-embedding-2` | تمثيل نصي للبحث؛ ليس توليد محتوى |
| `models/aqa` | غير محسوم |
| `models/gemini-3.5-transcribe-live` | كتابة نصوص واسكربتات |
| `models/gemini-2.5-flash-native-audio-latest` | كتابة نصوص واسكربتات |
| `models/gemini-2.5-flash-native-audio-preview-09-2025` | كتابة نصوص واسكربتات |
| `models/gemini-2.5-flash-native-audio-preview-12-2025` | كتابة نصوص واسكربتات |
| `models/gemini-3.1-flash-live-preview` | كتابة نصوص واسكربتات |
| `models/gemini-3.8-live` | كتابة نصوص واسكربتات |
| `models/gemini-3.8-live-extended-thinking` | كتابة نصوص واسكربتات |
| `models/gemini-robotics-er-2-streaming-preview` | كتابة نصوص واسكربتات |
| `models/gemini-3.5-live-translate-preview` | كتابة نصوص واسكربتات |
| `models/lyria-realtime-exp` | غير محسوم |

### groq — GROQ-01, GROQ-02

تطابقت مجموعات المعرفات بين المفاتيح الناجحة.

| المعرّف | التصنيف الآلي الأولي |
|---|---|
| `allam-2-7b` | غير محسوم |
| `canopylabs/orpheus-v1-english` | تعليق صوتي |
| `whisper-large-v3` | تفريغ صوت |
| `whisper-large-v3-turbo` | تفريغ صوت |
| `meta-llama/llama-prompt-guard-2-86m` | كتابة نصوص واسكربتات |
| `openai/gpt-oss-safeguard-20b` | كتابة نصوص واسكربتات |
| `openai/gpt-oss-120b` | كتابة نصوص واسكربتات |
| `meta-llama/llama-prompt-guard-2-22m` | كتابة نصوص واسكربتات |
| `canopylabs/orpheus-arabic-saudi` | تعليق صوتي |
| `qwen/qwen3.8-27b` | كتابة نصوص واسكربتات |
| `openai/gpt-oss-20b` | كتابة نصوص واسكربتات |

## ملفات التفاصيل وحدود الأمان

- `.runtime/provider-audit/report.md`: كل مفتاح ونماذجه/أصواته على حدة.
- `.runtime/provider-audit/report.json`: البيانات المنقحة للتحليل؛ ليست إعدادات إنتاج جاهزة.
- `.runtime/provider-audit/candidates.json`: قائمة فارغة لأن أي توليد مجاني لم يجتز اختبارًا بعد.
- لم تُكتب قيم المفاتيح الأصلية في ملفات المستودع أو مخرجات الفحص. نُقل ظرف مشفّر فقط بمفتاح خاص مؤقت على عامل GitHub، ثم نُظّف المفتاح الخاص.
- حُذف الظرف المستهلك من شجرة الفرع؛ تبقى نسخته المشفّرة في تاريخ Git. التقرير المنقح علني، ولا يحوي معرّفات حسابات أو بريدًا أو قيم مفاتيح.
- مفاتيح سبق نشرها في المحادثة: يُنصح بتدويرها بعد الاختبار. لم تُنسخ إلى Google Drive.
