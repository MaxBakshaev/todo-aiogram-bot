.SILENT:

# Переменная с вызовом docker-compose
DC = docker-compose -f docker/docker-compose.yml

# 🐳 Команды с docker-compose:

# Запуск docker-compose без аргументов
dc:
	$(DC)

# Запуск контейнеров
start:
	$(DC) start

# Поднятие с пересборкой в фоновом режиме и удалением образов <none>
restart:
	$(DC) down && $(DC) up --build -d && docker image prune -f

# Остановка контейнеров
stop:
	$(DC) stop

# Поднятие контейнеров в фоновом режиме
up:
	$(DC) up -d

# Поднятие контейнеров с логами
uplog:
	$(DC) up

# Сборка образов
build:
	$(DC) build

# Поднятие с пересборкой в фоновом режиме
bup:
	$(DC) up --build -d

# Поднятие с пересборкой и логами
buplog:
	$(DC) up --build

# Остановка и удаление контейнеров 
down:
	$(DC) down

# Остановка и удаление контейнеров и томов
downv:
	$(DC) down -v

# Удаление всех контейнеров, сетей, томов и образов
clean:
	$(DC) down --volumes --rmi all
	
# Удаление образов <none>
none:
	docker image prune -f

# Просмотр логов в реальном времени
logs:
	$(DC) logs -f

# Просмотр запущенных контейнеров
ps:
	$(DC) ps

# 🐍 Проверка кода по flake8
lint:
	flake8 core bot --max-line-length=79 --exclude=migrations && \
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