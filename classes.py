from abc import ABC, abstractmethod

class available_service_model(object):
    def __init__(self, name, module_path, specific_model_name, description):
        self.name = name
        self.module_path = module_path
        self.specific_model_name = specific_model_name
        self.description = description

class model_service_abstract(ABC):
    @abstractmethod
    def load_model(self, specific_model_name):
        pass

    @abstractmethod
    def run_inference(self, image_path, prompt):
        pass

    @abstractmethod
    def close_model(self):
        pass

class caption_directory_job:
    file_statuses = {}
    total_files = 0
    processed_files = 0
    captioned_files = 0
    error_count = 0

    def __init__(self, files):
        self.total_files = len(files)
        for file in files:
            self.file_statuses[file] = {}
    
    def update_file_status(self, file, status, message):
        self.file_statuses[file] = {'status': status, 'message': message}
        match status:
            case "Success":
                self.captioned_files += 1
            case "Error":
                self.error_count += 1
            case "Processing":
                self.processed_files += 1
    
    def get_progress(self):
        return {
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "captioned_files": self.captioned_files,
            "error_count": self.error_count,
            "file_statuses": self.file_statuses
        }