from .webserver import create_app
from .seed import create_tables


def main():
    create_tables()
    app = create_app()
    app.run("0.0.0.0", 5000)


if __name__ == "__main__":
    main()
