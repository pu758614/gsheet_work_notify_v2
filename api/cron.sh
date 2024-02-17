
#取得現在檔案路徑的路徑
DIR=$(cd $(dirname $0); pwd)

python $DIR/../daily_notify.py
