from johansencoint import analyze_cointegration

# Define the sets of stocks to analyze
stock_sets = [
    ["PEP", "KO", "PG"],      # Example set 1
    ["UL", "CCEP", "KO"],     # Example set 2
    ["MCD", "YUM", "WMT"],    # Example set 3
    ["JNJ", "PFE", "MRK"],    # Example set 4
    ["XOM", "CVX", "COP"],    # Example set 5
    ["PEP", "KO"],                      # Set 1: 2 stocks
    ["PG", "UL", "CCEP"],               # Set 2: 3 stocks
    ["MCD", "YUM", "WMT", "TGT"],       # Set 3: 4 stocks
    ["JNJ", "PFE", "MRK"],              # Set 4: 3 stocks
    ["XOM", "CVX", "COP", "BP", "SHEL"], # Set 5: 5 stocks
    ["GOOGL", "MSFT"],                  # Set 6: 2 stocks
    ["AAPL", "AMZN", "NFLX", "META"],   # Set 7: 4 stocks
    ["DIS", "CMCSA", "NFLX"],           # Set 8: 3 stocks
    ["TSLA", "GM", "F", "RIVN"],        # Set 9: 4 stocks
    ["BA", "GE", "LMT", "RTX", "NOC"]   # Set 10: 5 stocks
]

# Parameters for cointegration analysis
k = 2.5  # Multiplier for standard deviation in Z-score thresholds
lookback = 60  # Rolling window for mean and std

# Z-score thresholds for trading
z_upper_threshold = k  # +2.5
z_lower_threshold = -k  # -2.5

# Iterate over each set of stocks
for i, symbols in enumerate(stock_sets):
    print(f"\nAnalyzing Set {i+1}: {symbols}")
    
    try:
        # Call analyze_cointegration for the current set
        current_spread, current_z, beta_vector, is_cointegrated = analyze_cointegration(symbols, k=k, lookback=lookback)

        # Print the analysis results
        print("------------------------------------------------")
        print(f"Symbols: {symbols}")
        print("Beta Vector:", beta_vector)
        print(f"Current Spread: {current_spread:.4f}")
        print(f"Current Z-Score: {current_z:.4f}")
        print(f"Are the symbols cointegrated? {'Yes' if is_cointegrated else 'No'}")

        # Determine if a trade signal exists
        if is_cointegrated:
            if current_z > z_upper_threshold:
                print(f"Trading Signal: SHORT the spread for symbols {symbols}")
                print("Weights (Beta Vector):", beta_vector)
            elif current_z < z_lower_threshold:
                print(f"Trading Signal: LONG the spread for symbols {symbols}")
                print("Weights (Beta Vector):", beta_vector)
            else:
                print("No trade signal. Spread is within thresholds.")
        else:
            print("No trading signal as the symbols are not cointegrated.")

    except Exception as e:
        print(f"Error occurred during analysis for set {i+1}: {e}")
