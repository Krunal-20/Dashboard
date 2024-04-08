from base import db
from base.com.vo.detection_vo import FileVO, PotholeVO, CattleVO

# Query for files data
class FileDAO:
    def insert_file(self, file_vo):
        db.session.add(file_vo)
        db.session.commit()

    def get_file_id(self, infer_file):
        file_vo = FileVO.query.filter_by(file_name=infer_file).first()
        return file_vo.file_id
    
    def check_file_exists(self, filename):
        existing_file = FileVO.query.filter_by(file_name=filename).first()
        return existing_file is not None

    def get_file_data(self, file_id):
        file_vo = FileVO.query.filter_by(file_id=file_id).all()
        return file_vo


# Query for Potholes data   
class PotholeDAO:
    def insert_data(self, pothole_vo):
        db.session.add(pothole_vo)
        db.session.commit()

    def get_file_data(self, file_id):
        pothole_vo_list = db.session.query(
            PotholeVO, FileVO).filter(
                PotholeVO.pothole_file_id == FileVO.file_id,
                FileVO.file_id == file_id).all()
        return pothole_vo_list

 
# Query for Cattles data   
class CattleDAO:
    def insert_data(self, cattle_vo):
        db.session.add(cattle_vo)
        db.session.commit()

    def get_file_data(self, file_id):
        cattle_vo_list = db.session.query(
            CattleVO, FileVO).filter(
                CattleVO.cattle_file_id == FileVO.file_id,
                FileVO.file_id == file_id).all()
        return cattle_vo_list