from src.processing.cdti.pipeline import CDTIProcessingPipeline


class ProcessingPipeline:

    def __init__(self):
        pass

    
    def run_pipeline(self):
        # Initialize the CDTI processing pipeline
        cdti_processing_pipeline = CDTIProcessingPipeline()
        
        # Run the CDTI processing pipeline
        _ = cdti_processing_pipeline.run_pipeline()
        

    
