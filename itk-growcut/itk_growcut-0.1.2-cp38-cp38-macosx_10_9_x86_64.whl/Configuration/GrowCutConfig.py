depends = ('ITKPyBase', 'ITKSpatialObjects', 'ITKImageGrid', 'ITKCommon', )
templates = (
  ('FastGrowCut', 'itk::FastGrowCut', 'itkFastGrowCutISS3IUC3', True, 'itk::Image< signed short,3 >,itk::Image< unsigned char,3 >'),
  ('FastGrowCut', 'itk::FastGrowCut', 'itkFastGrowCutIUC3IUC3', True, 'itk::Image< unsigned char,3 >,itk::Image< unsigned char,3 >'),
  ('FastGrowCut', 'itk::FastGrowCut', 'itkFastGrowCutIUS3IUC3', True, 'itk::Image< unsigned short,3 >,itk::Image< unsigned char,3 >'),
  ('FastGrowCut', 'itk::FastGrowCut', 'itkFastGrowCutIF3IUC3', True, 'itk::Image< float,3 >,itk::Image< unsigned char,3 >'),
  ('FastGrowCut', 'itk::FastGrowCut', 'itkFastGrowCutID3IUC3', True, 'itk::Image< double,3 >,itk::Image< unsigned char,3 >'),
)
