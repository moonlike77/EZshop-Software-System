from app.models.DAO.return_dao import ReturnDAO

class ReturnRepository:
    # این خط باعث می‌شود دیتابیس در حافظه ساخته شود و ارور db ندهد
    _db_returns = {}
    _id_counter = 1

    def __init__(self):
        pass

    def create_return_transaction(self, new_return):
        new_return.return_id = ReturnRepository._id_counter
        ReturnRepository._db_returns[new_return.return_id] = new_return
        ReturnRepository._id_counter += 1
        return new_return.return_id

    def get_return_by_id(self, return_id):
        return ReturnRepository._db_returns.get(return_id)

    def update_return(self, return_obj):
        if return_obj.return_id in ReturnRepository._db_returns:
            ReturnRepository._db_returns[return_obj.return_id] = return_obj
            return True
        return False

    def delete_return(self, return_id):
        if return_id in ReturnRepository._db_returns:
            del ReturnRepository._db_returns[return_id]
            return True
        return False
        
    def get_all_returns(self):
        return list(ReturnRepository._db_returns.values())

    @classmethod
    def clear_db(cls):
        cls._db_returns = {}
        cls._id_counter = 1