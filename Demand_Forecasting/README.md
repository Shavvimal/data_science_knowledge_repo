TFT
Multi Horizon Forecast Model 
Models (e.g., DeepAR, MQRNN) have focused on variants of recurrent neural networks (RNNs), recent improvements, including Transformer-based models, have used attention-based layers
These do not consider the different inputs commonly present in multi-horizon forecasting and either assume that all exogenous inputs are known into the future or neglect important static covariates.
WHY USE?
TFT is designed to explicitly align the model with the general multi-horizon forecasting task for both superior accuracy and interpretability, which we demonstrate across various use cases.
Multi Horizon Forecast – can generate predictions for Market Trend
Benefits
Variable selection networks - to select relevant input variables at each time step.
Gating mechanisms to skip over any unused components of the model (learned from the data),
 static features to control how temporal dynamics are modeled., e.g., a location
conventional time series models are controlled by complex nonlinear interactions between many parameters, making it difficult to explain how such models arrive at their predictions.  - Interpretability 
Multi-horixon forecasting – Predict overall Market

 
TFT outperforms all benchmarks over a variety of datasets.
