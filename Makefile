.SILENT:

# 🐍 Проверка кода по flake8
lint:
	flake8 core --max-line-length=79 --exclude=migrations && \
	echo "Lint: SUCCESS" || (echo "Lint: FAIL" && exit 1)

# ➤ 📄 Экспорт зависимостей poetry в requirements.txt
req:
	poetry export --without-hashes -f requirements.txt -o requirements.txt

# 🔄 Обновить dev ветку из main с ребейзом и пушем
update-dev:
	@git checkout main
	@git pull origin main
	@git checkout dev
	@git rebase main
	@git push --force-with-lease

# 🔩 Запуск celery воркера и вывод логгов в консоль
celery:
	celery -A core.project worker --loglevel=info