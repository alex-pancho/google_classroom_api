import logging
import sys
import io
import codecs

# Override stdout and stderr to support UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
utf8_stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
file_handler = logging.FileHandler("google_class.log", encoding="utf8")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[file_handler, logging.StreamHandler(utf8_stdout)],
)
logger = logging.getLogger(__name__)