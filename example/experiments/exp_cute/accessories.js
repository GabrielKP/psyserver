"use strict";
/* eslint-disable no-unused-vars */

// in-place Fisher-Yates (or Durstenfeld) shuffle
function shuffleArray(array) {
    let swapTo = array.length; // index of position to swap to
    let swapFrom = null; // index of element randomly selected to swap
    let temp = null; // holds a value for changing assignment
    // work back to front, swapping with random unswapped (earlier) elements
    while (swapTo > 0) {
        // pick an (unswapped) element from the back
        swapFrom = Math.floor(Math.random() * swapTo--);
        // swap it with the current element
        temp = array[swapTo];
        array[swapTo] = array[swapFrom];
        array[swapFrom] = temp;
    }
}

// return whether two scalar arrays have the same values (in any order)
function sameValues(array1, array2) {
    let sameLength = array1.length === array2.length;
    let allThere = array1.every(value => array2.includes(value));
    return sameLength && allThere;
}

function objectCartesian(templateObject) {
    function nArrayCartesian(arrays) {
        function twoArrayCartesian(array1, array2) {
            return [].concat(...array1.map((array1Elem) => {
                return array2.map((array2Elem) => {
                    return [].concat(array1Elem, array2Elem);
                });
            }));
        }
        if (arrays[1]) {
            let firstTwo = [twoArrayCartesian(arrays[0], arrays[1])];
            return nArrayCartesian(firstTwo.concat(arrays.slice(2)));
        }
        return arrays[0];
    }

    let templateKeys = Object.keys(templateObject);
    let templateValues = Object.values(templateObject);
    let cartesianValues = nArrayCartesian(templateValues);

    let outputArray = cartesianValues.map((particularValues) => {
        let currentObject = {};
        templateKeys.forEach((key, index) => {
            currentObject[key] = particularValues[index];
        });
        return currentObject;
    });
    return outputArray;
}
