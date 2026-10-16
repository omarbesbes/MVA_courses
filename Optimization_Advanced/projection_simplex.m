%--------------------------------------------------------------------------
function [ w ] = projection_simplex( p )
%--------------------------------------------------------------------------
%PROJECTION computes the point in the 
%unit simplex conv(e_1,...,e_n) with minimal distance
%to an arbitrary given point.
%
% p \in R^mn,Q
%p must be a row vector


[mn,Q] = size(p);

%projection of p on hyperplane w_1 + ... + w_n = 1
lambda = (sum(p,2)-1)/Q;
w = p-lambda*ones(1,Q);

subzerodetect = zeros(mn,Q);
subzerodetect(w<0) = 1;

while(sum(subzerodetect(:)) > 0)
    % while projection is not in the simplex:
    % project orthogonally on to the corresponding coordinate hyperplane and
    % and project along the corresponding direction on to the simplex
    direction = zeros(mn,Q);
    direction(w>0) = 1;
    w(w<0)=0;
    
    denominator = sum(direction,2);
    lambda = (sum(w,2)-1) ./ denominator;
    
    w = w - lambda * ones(1,Q) .* direction;
    subzerodetect = zeros(mn,Q);
    subzerodetect(w<0) = 1;
end