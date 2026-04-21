#!/usr/bin/env python3
"""
Скрипт для отслеживания и убийства процессов на порту 20128.
Можно запускать вручную, по cron или как демон.
"""

import logging
import subprocess
import sys
import time
from pathlib import Path

PORT = 20128
LOG_FILE = "/tmp/kill_port_20128_py.log"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_pids_on_port(port):
    """Возвращает список PID процессов, использующих порт."""
    try:
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return [int(pid) for pid in result.stdout.strip().split() if pid.isdigit()]
        return []
    except subprocess.TimeoutExpired:
        logger.error("Таймаут при выполнении lsof")
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении PID: {e}")
        return []

def kill_pids(pids):
    """Убивает процессы по списку PID."""
    killed = []
    for pid in pids:
        try:
            # Получаем информацию о процессе
            proc_info = subprocess.run(
                ['ps', '-p', str(pid), '-o', 'pid,cmd', '--no-headers'],
                capture_output=True,
                text=True
            ).stdout.strip() or f"PID {pid}"
            
            logger.info(f"Убиваем процесс {pid}: {proc_info}")
            subprocess.run(['kill', '-9', str(pid)], timeout=5)
            killed.append(pid)
            logger.info(f"Процесс {pid} успешно убит")
        except subprocess.TimeoutExpired:
            logger.error(f"Таймаут при убийстве процесса {pid}")
        except Exception as e:
            logger.error(f"Не удалось убить процесс {pid}: {e}")
    
    return killed

def use_fuser(port):
    """Использует fuser для убийства процессов на порту."""
    try:
        result = subprocess.run(
            ['fuser', '-k', f'{port}/tcp'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info(f"fuser завершил процессы на порту {port}")
            return True
    except Exception as e:
        logger.error(f"Ошибка при использовании fuser: {e}")
    return False

def main(continuous=False, interval=10):
    """Основная функция."""
    logger.info(f"Запуск мониторинга порта {PORT}")
    
    while True:
        pids = get_pids_on_port(PORT)
        
        if pids:
            logger.warning(f"Найдены процессы на порту {PORT}: {pids}")
            killed = kill_pids(pids)
            
            # Дополнительно используем fuser для надёжности
            use_fuser(PORT)
            
            # Проверяем остались ли процессы
            remaining = get_pids_on_port(PORT)
            if remaining:
                logger.error(f"ВНИМАНИЕ: остались процессы на порту {PORT}: {remaining}")
            else:
                logger.info(f"Порт {PORT} полностью освобождён")
        else:
            logger.debug(f"Нет процессов на порту {PORT}")
        
        if not continuous:
            break
        
        time.sleep(interval)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Убийство процессов на порту 20128')
    parser.add_argument('--continuous', '-c', action='store_true',
                       help='Непрерывный мониторинг с указанным интервалом')
    parser.add_argument('--interval', '-i', type=int, default=10,
                       help='Интервал в секундах для непрерывного мониторинга (по умолчанию: 10)')
    parser.add_argument('--log-level', '-l', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Уровень логирования')
    
    args = parser.parse_args()
    
    # Устанавливаем уровень логирования
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        main(continuous=args.continuous, interval=args.interval)
    except KeyboardInterrupt:
        logger.info("Скрипт остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)