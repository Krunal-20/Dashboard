from base import db, app
from flask_migrate import Migrate
migrate = Migrate(app, db)

class FileVO(db.Model):
    __tablename__ = 'file_info'
    file_id = db.Column('file_id', db.Integer, autoincrement=True, primary_key=True)
    file_save_path = db.Column('file_save_path', db.String(255),
                               nullable=False)
    file_output_path = db.Column('file_output_path', db.String(255),
                                 nullable=False)
    file_name = db.Column('file_name', db.String(255), nullable=False, unique=True)
    file_type = db.Column('file_type', db.String(255), nullable=False)
    model = db.Column('model', db.String(255), nullable=False)

    def as_dict(self):
        return {
            'file_id': self.file_id,
            'file_save_path': self.file_save_path,
            'file_output_path': self.file_output_path,
            'file_type': self.file_type,
            'model': self.model,
        }


class PotholeVO(db.Model):
    __tablename__ = 'pothole_info'
    result_id = db.Column('result_id', db.Integer, autoincrement=True, primary_key=True)
    pothole_file_id = db.Column('pothole_file_id', db.Integer, db.ForeignKey(FileVO.file_id,
                                                      ondelete='CASCADE',
                                                      onupdate='CASCADE'), nullable=False)
    frame_id = db.Column('frame_id', db.Integer, nullable=True)
    pothole_counts = db.Column('pothole_counts', db.Integer, nullable=False)

    def as_dict(self):
        return {
            'result_id': self.result_id,
            'pothole_file_id': self.pothole_file_id,
            'frame_id': self.frame_id,
            'pothole_counts': self.pothole_counts,
        }


class CattleVO(db.Model):
    __tablename__ = 'cattle_info'
    result_id = db.Column('result_id', db.Integer, autoincrement=True, primary_key=True)
    cattle_file_id = db.Column('cattle_file_id', db.Integer, db.ForeignKey(FileVO.file_id,
                                                      ondelete='CASCADE',
                                                      onupdate='CASCADE'), nullable=False)
    frame_id = db.Column('frame_id', db.Integer, nullable=True)
    cattle_counts = db.Column('cattle_counts', db.Integer, nullable=False)

    def as_dict(self):
        return {
            'result_id': self.result_id,
            'cattle_file_id': self.cattle_file_id,
            'frame_id': self.frame_id,
            'cattle_counts': self.cattle_counts,
        }

with app.app_context():
    db.create_all()