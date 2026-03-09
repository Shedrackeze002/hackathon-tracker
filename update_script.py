from datetime import datetime, timedelta


def main():
    # Compute Kigali time (UTC+2)
    now_utc = datetime.utcnow() + timedelta(hours=2)
    date_str = now_utc.strftime("%Y-%m-%d %H:%M:%S")
    with open("last_updated.txt", "w") as f:
        f.write(f"Last updated: {date_str} Africa/Kigali\n")


if __name__ == "__main__":
    main()
