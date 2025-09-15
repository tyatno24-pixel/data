// Calculator Functions
let currentInput = '0';
let operator = null;
let previousInput = '';
let resetScreen = false;

function updateCalculatorOutput() {
    document.getElementById('calculatorOutput').value = currentInput;
}

function appendCharacter(char) {
    if (resetScreen) {
        currentInput = char;
        resetScreen = false;
    } else if (currentInput === '0' && char !== '.') {
        currentInput = char;
    } else {
        currentInput += char;
    }
    updateCalculatorOutput();
}

function chooseOperator(nextOperator) {
    if (currentInput === '0' && previousInput === '') return; // Don't set operator if nothing entered

    if (previousInput !== '') {
        calculateResult();
    }
    operator = nextOperator;
    previousInput = currentInput;
    currentInput = '0'; // Reset current input for next number
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
    const prev = parseFloat(previousInput);
    const current = parseFloat(currentInput);

    if (isNaN(prev) || isNaN(current) || operator === null) return;

    switch (operator) {
        case '+':
            result = prev + current;
            break;
        case '-':
            result = prev - current;
            break;
        case '*':
            result = prev * current;
            break;
        case '/':
            if (current === 0) {
                alert("Cannot divide by zero!");
                clearCalculator();
                return;
            }
            result = prev / current;
            break;
        default:
            return;
    }
    currentInput = result.toString();
    operator = null;
    previousInput = '';
    resetScreen = true; // After calculation, next number should clear screen
    updateCalculatorOutput();
}

function initCalculator() {
    // Any initialization specific to the calculator page can go here
    // For example, ensuring the output is reset when the page is shown
    clearCalculator();
}