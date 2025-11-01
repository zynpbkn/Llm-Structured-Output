🤖  LangChain Structured Output & JSONL Logging
Bu proje, müşteri destek taleplerini içeren bir CSV dosyasını okur ve Google Gemini 2.5 Flash LLM'ini kullanarak her bir talebi önceden tanımlanmış katı bir Pydantic şemasına göre analiz ederek yapılandırılmış veriye dönüştürür. Çıkarılan veriler, hem konsola (pretty-print) hem de append-safe JSONL formatında bir log dosyasına yazılır.

✨ Temel Özellikler
Amaç: Destek talebi metinlerinden, Pydantic ile onaylanmış katı yapıda veriler çıkarmak.

LLM & Entegrasyon: LangChain'in with_structured_output metodu, Gemini 2.5 Flash ile entegre edilerek yapısal çıktı garantisi verilir.

Hata Yönetimi: LLM çağrılarında olası hatalara karşı tekrar deneme (retry) mekanizması (max_retries = 2) mevcuttur.

Loglama: Başarılı çıkarımlar, logs/outputs.jsonl dosyasına yazılırken, her kayda run_id ve source_id gibi ek metadata dahil edilir.
📂 Proje Yapısı
.
├── .env                   
├── support_tickets_minimal.csv  # **Girdi CSV dosyası**
├── requirements.txt
├── README.md
├── app                     # Uygulama modülleri
│   ├── __init__.py
│   ├── llm_chain.py
│   ├── main.py
│   └── models.py
└── logs
    ├── outputs.jsonl       # LLM çıktılarının loglandığı dosya
    └── run.log
🛠️ LLM Pipeline Detayları (app/llm_chain.py)
Projenin kalbi olan LLM pipeline'ı, TicketExtraction Pydantic modelini kullanarak çıktıyı zorlar.

Prompt Mühendisliği
Sistem prompt'u, Gemini modeline kısıtlamaları, zorunlu alanları ve Enum değerlerini kesin bir dille belirtir:

Python

SYSTEM = (
    "You are a strict information extractor. Return JSON with EXACTLY these keys: "
    "issue_type, urgency, channel, entities, summary, status_suggestion. "
    # ... [Devam eden kısıtlamalar]
    "Do NOT add extra fields. Return JSON only."
)
Yapılandırılmış Çıktı
LangChain'in with_structured_output(TicketExtraction) metodu, LLM çıktısını otomatik olarak TicketExtraction Pydantic modeline dönüştürmeyi garantiler.

Python

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
chain: Runnable = prompt | llm.with_structured_output(TicketExtraction)
Veri Temizleme (Normalization)
extract_ticket fonksiyonu, amount alanını LLM'den alındıktan sonra (string, int veya float olabilir) standart bir float değere dönüştürmek için özel bir temizleme (_normalize_amount_like) adımı içerir.

🎯 Pydantic Şemaları (app/models.py)
Kullanılan Enum'lar ve iç içe geçmiş alanlar dahil Pydantic modeli:

Python

# Kısıtlı Enum'lar ve Optional alanlar ile doğru tanımlanmıştır.
# ...
class Entities(BaseModel):
    amount: Optional[float] = Field(default=None, description="Numeric amount, e.g., 49.99")
    # ... diğer alanlar
class TicketExtraction(BaseModel):
    issue_type: Literal["billing","technical","account","general"]
    # ... diğer ana alanlar
⚙️ Kurulum ve Çalıştırma Adımları
Adım 1: Bağımlılıkları Yükleme
Bash

python3 -m venv venv
source .venv/bin/activate
uv add -r requirements.txt
Adım 2: API Anahtarını Ayarlama
GOOGLE_API_KEY'i içeren .env dosyasını proje ana dizininde oluşturun.

Adım 3: Uygulamayı Çalıştırma
CSV dosyasının yolunu argüman olarak vererek uygulamayı çalıştırın:

Bash

python -m app.main ./support_tickets_minimal.csv




Bash

python -m app.main ./support_tickets_minimal.csv
