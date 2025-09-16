// Calculator Functions
let currentInput = '0';
let operator = null;
let previousInput = '';
let resetScreen = false;

function updateCalculatorOutput() {
    document.getElementById('calculatorOutput').value = currentInput;
}

function appendCharacter(char) {
    // Handle operator clicks
    if (['+', '-', '*', '/'].includes(char)) {
        chooseOperator(char);
        return;
    }

    // Handle number and decimal clicks
    if (resetScreen) {
        currentInput = char;
        resetScreen = false;
    } else if (currentInput === '0' && char !== '.') {
        currentInput = char;
    } else {
        // Prevent multiple decimals
        if (char === '.' && currentInput.includes('.')) {
            return;
        }
        currentInput += char;
    }
    updateCalculatorOutput();
}

function chooseOperator(nextOperator) {
    if (currentInput === '' && previousInput === '') return;

    // If there's already a previous number and an operator, calculate first
    if (operator !== null) {
        calculateResult();
    }
    operator = nextOperator;
    previousInput = currentInput;
    resetScreen = true;
}

function clearCalculator() {
    currentInput = '0';
    operator = null;
    previousInput = '';
    resetScreen = false;
    updateCalculatorOutput();
}

function calculateResult() {
    let result;
    if (operator === null || previousInput === '' || currentInput === '') return;

    const prev = parseFloat(previousInput);
    const current = parseFloat(currentInput);

    switch (operator) {
        case '+': result = prev + current; break;
        case '-': result = prev - current; break;
        case '*': result = prev * current; break;
        case '/':
            if (current === 0) {
                alert("Cannot divide by zero!");
                clearCalculator();
                return;
            }
            result = prev / current;
            break;
        default: return;
    }
    currentInput = result.toString();
    operator = null;
    previousInput = ''; // Reset previous input after calculation
    resetScreen = true; // After calculation, next number should clear screen
    updateCalculatorOutput();
}

function initCalculator() {
    // This function can be used to set up event listeners if needed in the future.
    // For now, it's a placeholder.
    updateCalculatorOutput();
}