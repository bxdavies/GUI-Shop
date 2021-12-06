################
# Module Files #
################
from app import main

#############
# Libraries #
#############
from dotenv import load_dotenv

###############
# Entry Point #
###############
if __name__ == "__main__":
    load_dotenv()
    main.main()