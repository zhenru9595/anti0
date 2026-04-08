import datetime

def calculate_days():
    print("=== 살아온 날짜 계산기 ===")
    birthday_str = input("생년월일을 입력하세요 (예: 1990-01-01): ")
    try:
        # 입력받은 문자열을 날짜 객체로 변환
        birthday = datetime.datetime.strptime(birthday_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        
        # 미래의 날짜인지 확인
        if birthday > today:
            print("미래의 날짜입니다. 올바른 생년월일을 입력해주세요.")
            return
            
        # 살아온 날짜 계산
        days_lived = (today - birthday).days
        
        print(f"\n태어난 지 {days_lived:,}일이 지났습니다.")
        
    except ValueError:
        print("잘못된 형식입니다. YYYY-MM-DD (예: 1990-01-01) 형식으로 입력해주세요.")

if __name__ == "__main__":
    calculate_days()
    input("\n엔터를 누르면 종료됩니다...")
