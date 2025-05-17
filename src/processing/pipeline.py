from src.processing.cdti.pipeline import CDTIProcessingPipeline


class ProcessingPipeline:
    """
    A class to represent a processing pipeline.
    Methods
    -------
    run_pipeline():
        Executes the CDTI processing pipeline.
    """

    def __init__(self):
        pass

    
    def run_pipeline(self):
        # Initialize the CDTI processing pipeline
        cdti_processing_pipeline = CDTIProcessingPipeline()
        
        # Run the CDTI processing pipeline
        _ = cdti_processing_pipeline.run_pipeline()
        

    
