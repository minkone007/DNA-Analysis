getMonte <- function(datafile, targetfile) {
    # Load data
    ref <- read.csv(datafile, row.names = 1)
    target <- read.csv(targetfile, row.names = 1)
    
    # Ensure target is a vector
    target_vec <- as.numeric(target[1,])
    
    # Calculate Euclidean distances
    dists <- apply(ref, 1, function(x) sqrt(sum((as.numeric(x) - target_vec)^2)))
    
    # Create final_result
    final_result <<- sort(dists)
    
    return(final_result)
}
