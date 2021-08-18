from pipeline.pipeline import generatedProjectNamePipeline

if __name__ == '__main__':
    p = generatedProjectNamePipeline()
    output = p.execute()
    print(output)
