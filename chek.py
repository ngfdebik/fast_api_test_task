import re
import os

def fix_test_files():
    tests_dir = "tests"
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 1. Удаляем test_session_factory из параметров функций
                content = re.sub(r',\s*test_session_factory', '', content)
                content = re.sub(r'test_session_factory,\s*', '', content)
                
                # 2. Заменяем subdepartments на children
                content = content.replace('subdepartments', 'children')
                content = content.replace('"subdepartments"', '"children"')
                content = content.replace("'subdepartments'", "'children'")
                
                # 3. Исправляем вызовы create_department - передаем правильную сессию
                # Заменяем create_department(test_session_factory, ...) на create_department(db_session, ...)
                content = re.sub(
                    r'create_department\(test_session_factory,',
                    'create_department(db_session,',
                    content
                )
                content = re.sub(
                    r'create_department\(\s*test_session_factory\s*,',
                    'create_department(db_session,',
                    content
                )
                
                # 4. Исправляем create_employee
                content = re.sub(
                    r'create_employee\(test_session_factory,',
                    'create_employee(db_session,',
                    content
                )
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed: {filepath}")

if __name__ == "__main__":
    fix_test_files()
    print("\n✅ Все исправления применены!")
    print("Запустите тесты снова: pytest tests/ -v")