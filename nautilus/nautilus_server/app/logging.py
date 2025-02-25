import logging
import sys

nautilus_logo = r"""
 ███╗   ██╗ ██████╗██╗   ██╗████████╗██ ██╗     ██╗   ██╗███████╗
 ████╗  ██║██╔══██╗██║   ██║╚══██╔══╝██ ██║     ██║   ██║██╔════╝
 ██╔██╗ ██║███████║██║   ██║   ██║   ██ ██║     ██║   ██║███████╗
 ██║╚██╗██║██╔══██║██║   ██║   ██║   ██ ██║     ██║   ██║╚════██║
 ██║ ╚████║██║  ██║╚██████╔╝   ██║   ██ ███████╗╚██████╔╝███████║
 ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚╝ ╚══════╝ ╚═════╝ ╚══════╝
"""


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_logo():
    print(f"\n{nautilus_logo}\n")
    logging.info("🚀 Nautilus API is starting...")
