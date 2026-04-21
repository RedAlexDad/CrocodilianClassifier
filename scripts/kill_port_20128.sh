#!/bin/bash

# Скрипт для отслеживания и убийства процессов на порту 20128
PORT=20128
LOG_FILE="/tmp/kill_port_20128.log"

# Функция для логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Проверяем, есть ли процессы на порту
PIDS=$(lsof -ti:$PORT 2>/dev/null)

if [ -z "$PIDS" ]; then
    log "Нет процессов на порту $PORT"
    exit 0
fi

# Логируем найденные процессы
log "Найдены процессы на порту $PORT: $PIDS"

# Убиваем каждый процесс
for PID in $PIDS; do
    # Получаем информацию о процессе перед убийством
    PROCESS_INFO=$(ps -p "$PID" -o pid,cmd --no-headers 2>/dev/null || echo "unknown")
    log "Убиваем процесс $PID: $PROCESS_INFO"
    kill -9 "$PID" 2>/dev/null
    if [ $? -eq 0 ]; then
        log "Процесс $PID успешно убит"
    else
        log "Не удалось убить процесс $PID"
    fi
done

# Дополнительная проверка через fuser для надёжности
fuser -k "${PORT}/tcp" 2>/dev/null
if [ $? -eq 0 ]; then
    log "fuser завершил оставшиеся процессы на порту $PORT"
fi

# Финальная проверка
REMAINING=$(lsof -ti:$PORT 2>/dev/null)
if [ -z "$REMAINING" ]; then
    log "Порт $PORT полностью освобождён"
else
    log "ВНИМАНИЕ: остались процессы на порту $PORT: $REMAINING"
fi