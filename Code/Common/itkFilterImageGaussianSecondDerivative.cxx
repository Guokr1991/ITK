/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    itkFilterImageGaussianSecondDerivative.cxx
  Language:  C++
  Date:      $Date$
  Version:   $Revision$


  Copyright (c) 2000 National Library of Medicine
  All rights reserved.

  See COPYRIGHT.txt for copyright details.

=========================================================================*/
#include "itkFilterImageGaussianSecondDerivative.h"
#include "itkObjectFactory.h"


//------------------------------------------------------------------------
template <class TInputImage, class TOutputImage, class TComputation>
itkFilterImageGaussianSecondDerivative<TInputImage,TOutputImage, TComputation>::Pointer 
itkFilterImageGaussianSecondDerivative<TInputImage,TOutputImage, TComputation>
::New()
{
  itkFilterImageGaussianSecondDerivative<TInputImage,TOutputImage,TComputation>* ret = 
    itkObjectFactory< itkFilterImageGaussianSecondDerivative<TInputImage,TOutputImage,TComputation> >::Create();
  if ( ! ret )
  {
    ret = new itkFilterImageGaussianSecondDerivative< TInputImage, TOutputImage, TComputation >();
  }
  
  return ret;

}



//----------------------------------------
//   Compute filter for Gaussian kernel
//----------------------------------------
template <class TInputImage, class TOutputImage, class TComputation>
void itkFilterImageGaussianSecondDerivative<TInputImage,TOutputImage, TComputation>
::SetUp(TComputation dd)
{

  a0 = TComputation( -1.3310 );
	a1 = TComputation(  3.6610 );
	b0 = TComputation(  1.2400 );
	b1 = TComputation(  1.3140 );
	c0 = TComputation(  0.3225 );
	c1 = TComputation( -1.7380 );
	w0 = TComputation(  0.7480 );
	w1 = TComputation(  2.1660 );

	const TComputation sigmad = cSigma/dd;
//K = 1.0/(sigmad*sigmad*sqrt(2.0*(4.0*atan(1.0))));
	K = 1.0 / ( sigmad * sqrt( 2.0 * ( 4.0 * atan( 1.0 ) ) ) );

	const bool symmetric = true;
	ComputeFilterCoefficients(symmetric);

}



