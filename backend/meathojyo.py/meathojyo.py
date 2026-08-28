from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="食事補助ポイント管理API", version="4.3.0")

# -----------------------------
# 1. データモデル
# -----------------------------

class User(BaseModel):
    user_id: str
    name: str
    balance: int = 0
    monthly_limit: int = 15000
    used: int = 0
    charged: int = 0
    last_charged_month: str = ""

class ChargeLog(BaseModel):
    user_id: str
    amount: int
    timestamp: datetime

class UseLog(BaseModel):
    user_id: str
    amount: int
    timestamp: datetime
    description: str

# -----------------------------
# 2. データベース
# -----------------------------

users_db = {
    "EMP001": User(
        user_id="EMP001",
        name="山田太郎",
        balance=0,
        monthly_limit=15000,
        used=0,
        charged=0,
        last_charged_month=""
    )
}

charge_logs: List[ChargeLog] = []
use_logs: List[UseLog] = []

# -----------------------------
# 3. 月リセット
# -----------------------------

def monthly_reset(user: User):
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    if user.last_charged_month != current_month:
        user.used = 0
        user.charged = 0
        user.last_charged_month = current_month

# -----------------------------
# 4. ユーザー登録
# -----------------------------

@app.post("/api/register")
def register_user(user: User):
    if user.user_id in users_db:
        raise HTTPException(status_code=400, detail="ユーザーは既に登録されています")

    user.balance = 0
    user.monthly_limit = 15000
    user.used = 0
    user.charged = 0
    user.last_charged_month = ""

    users_db[user.user_id] = user
    return {"status": "success", "message": f"{user.user_id} を登録しました"}

# -----------------------------
# 5. 残高確認
# -----------------------------

@app.get("/api/balance/{user_id}")
def get_balance(user_id: str):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")

    monthly_reset(user)

    return {
        "user_id": user.user_id,
        "name": user.name,
        "balance": user.balance,
        "used": user.used,
        "charged": user.charged,
        "monthly_limit": user.monthly_limit
    }

# -----------------------------
# 6. ポイント利用
# -----------------------------

class UseRequest(BaseModel):
    user_id: str
    amount: int
    description: str

@app.post("/api/use")
def use_points(req: UseRequest):
    user = users_db.get(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")

    monthly_reset(user)

    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="利用額が不正です")

    if req.amount > user.balance:
        raise HTTPException(status_code=400, detail="残高不足です")

    user.balance -= req.amount
    user.used += req.amount

    use_logs.append(
        UseLog(
            user_id=req.user_id,
            amount=req.amount,
            timestamp=datetime.now(),
            description=req.description
        )
    )

    return {
        "status": "success",
        "message": f"{req.amount} ポイントを利用しました",
        "remaining_balance": user.balance
    }

# -----------------------------
# 7. 月次チャージ
# -----------------------------

@app.post("/api/monthly-charge/{user_id}")
def monthly_charge(user_id: str):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")

    now = datetime.now()
    current_month = now.strftime("%Y-%m")

    charge_amount = 15000

    user.balance += charge_amount
    user.charged += charge_amount
    user.last_charged_month = current_month

    charge_logs.append(
        ChargeLog(
            user_id=user_id,
            amount=charge_amount,
            timestamp=now
        )
    )

    return {
        "status": "success",
        "message": f"{user_id} に {charge_amount} ポイントをチャージしました",
        "balance": user.balance
    }

# -----------------------------
# 8. ポイント付与（admin.py 用）
# -----------------------------

class AddRequest(BaseModel):
    user_id: str
    amount: int
    description: str = "会社付与"

@app.post("/api/add")
def add_points(req: AddRequest):
    user = users_db.get(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")

    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="付与額が不正です")

    user.balance += req.amount
    user.charged += req.amount

    charge_logs.append(
        ChargeLog(
            user_id=req.user_id,
            amount=req.amount,
            timestamp=datetime.now()
        )
    )

    return {
        "status": "success",
        "message": f"{req.amount} ポイントを付与しました",
        "balance": user.balance
    }

# -----------------------------
# 9. 従業員一覧
# -----------------------------

@app.get("/api/all-users")
def get_all_users():
    result = []
    for user_id, user in users_db.items():
        monthly_reset(user)
        result.append({
            "user_id": user.user_id,
            "name": user.name,
            "used": user.used,
            "charged": user.charged,
            "balance": user.balance
        })
    return result

# -----------------------------
# 10. 印刷用データ
# -----------------------------

@app.get("/api/print-users")
def print_users():
    table = []
    for user_id, user in users_db.items():
        monthly_reset(user)
        table.append([
            user.user_id,
            user.name,
            user.used,
            user.charged,
            user.balance
        ])
    return {
        "header": ["従業員ID", "氏名", "当月利用", "当月チャージ", "残ポイント"],
        "rows": table
    }

# -----------------------------
# 11. 利用履歴（従業員別）
# -----------------------------

@app.get("/api/use-log/{user_id}")
def get_use_log_by_user(user_id: str):
    logs = []
    for log in use_logs:
        if log.user_id == user_id:
            logs.append({
                "timestamp": log.timestamp.isoformat(),
                "amount": log.amount,
                "description": log.description
            })
    return logs

# -----------------------------
# 12. チャージ履歴
# -----------------------------

@app.get("/api/charge-log")
def get_charge_log():
    return charge_logs

# -----------------------------
# 13. 従業員削除
# -----------------------------

@app.delete("/api/delete/{user_id}")
def delete_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")
    del users_db[user_id]
    return {"status": "success", "message": f"{user_id} を削除しました"}

# -----------------------------
# 14. 従業員情報変更
# -----------------------------

class UpdateUser(BaseModel):
    name: Optional[str] = None
    balance: Optional[int] = None

@app.put("/api/update/{user_id}")
def update_user(user_id: str, data: UpdateUser):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")

    if data.name is not None:
        user.name = data.name
    if data.balance is not None:
        user.balance = data.balance

    return {"status": "success", "message": f"{user_id} を更新しました"}
