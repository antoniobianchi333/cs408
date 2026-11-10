package parser

import (
	"reflect"
	"testing"

	"github.com/abs-lang/abs/ast"
	"github.com/abs-lang/abs/lexer"
)

// parseSteppedSlice parses input and returns the IndexExpression of the
// first statement, failing the test if parsing produced errors or the
// statement is not an IndexExpression.
func parseSteppedSlice(t *testing.T, input string) *ast.IndexExpression {
	t.Helper()

	l := lexer.New(input)
	p := New(l)
	program := p.ParseProgram()
	checkParserErrors(t, p)

	if len(program.Statements) != 1 {
		t.Fatalf("program has %d statements. want=1", len(program.Statements))
	}

	stmt, ok := program.Statements[0].(*ast.ExpressionStatement)
	if !ok {
		t.Fatalf("statement is not *ast.ExpressionStatement. got=%T", program.Statements[0])
	}

	indexExp, ok := stmt.Expression.(*ast.IndexExpression)
	if !ok {
		t.Fatalf("exp not *ast.IndexExpression. got=%T", stmt.Expression)
	}

	return indexExp
}

// steppedSliceStep reads the Step field of the IndexExpression via
// reflection so that this test compiles even on a build of the AST that
// does not yet support stepped slices. A missing field produces a named
// failure instead of a compile error.
func steppedSliceStep(t *testing.T, exp *ast.IndexExpression) (float64, bool) {
	t.Helper()

	v := reflect.ValueOf(exp).Elem().FieldByName("Step")
	if !v.IsValid() {
		t.Fatalf("ast.IndexExpression has no Step field: stepped slices are not supported")
		return 0, false
	}
	if v.IsNil() {
		return 0, true
	}
	switch s := v.Interface().(type) {
	case *ast.NumberLiteral:
		return s.Value, true
	case *ast.PrefixExpression:
		if num, ok := s.Right.(*ast.NumberLiteral); ok {
			return -num.Value, true
		}
	}
	t.Fatalf("Step is not a number literal. got=%T", v.Interface())
	return 0, false
}

func TestParsingSteppedSliceExpressions(t *testing.T) {
	exp := parseSteppedSlice(t, "myArray[99 : 101 : 2]")

	if !exp.IsRange {
		t.Fatalf("exp is not range")
	}

	if !testIdentifier(t, exp.Left, "myArray") {
		return
	}

	testNumberLiteral(t, exp.Index, 99)
	testNumberLiteral(t, exp.End, 101)

	step, ok := steppedSliceStep(t, exp)
	if !ok {
		return
	}
	if step != 2 {
		t.Fatalf("step is not 2. got=%v", step)
	}
}

func TestParsingSteppedSliceWithoutStartExpressions(t *testing.T) {
	exp := parseSteppedSlice(t, "myArray[: 101 : 2]")

	if !exp.IsRange {
		t.Fatalf("exp is not range")
	}

	if !testIdentifier(t, exp.Left, "myArray") {
		return
	}

	testNumberLiteral(t, exp.Index, 0)
	testNumberLiteral(t, exp.End, 101)

	step, ok := steppedSliceStep(t, exp)
	if !ok {
		return
	}
	if step != 2 {
		t.Fatalf("step is not 2. got=%v", step)
	}
}

func TestParsingSteppedSliceWithoutEndExpressions(t *testing.T) {
	exp := parseSteppedSlice(t, "myArray[4 :: -1]")

	if !exp.IsRange {
		t.Fatalf("exp is not range")
	}

	if !testIdentifier(t, exp.Left, "myArray") {
		return
	}

	testNumberLiteral(t, exp.Index, 4)

	if exp.End != nil {
		t.Fatalf("range end is not nil. got=%T", exp.End)
	}

	step, ok := steppedSliceStep(t, exp)
	if !ok {
		return
	}
	if step != -1 {
		t.Fatalf("step is not -1. got=%v", step)
	}
}

func TestParsingSteppedSliceOnlyStepExpressions(t *testing.T) {
	exp := parseSteppedSlice(t, "myArray[::2]")

	if !exp.IsRange {
		t.Fatalf("exp is not range")
	}

	if !testIdentifier(t, exp.Left, "myArray") {
		return
	}

	testNumberLiteral(t, exp.Index, 0)

	if exp.End != nil {
		t.Fatalf("range end is not nil. got=%T", exp.End)
	}

	step, ok := steppedSliceStep(t, exp)
	if !ok {
		return
	}
	if step != 2 {
		t.Fatalf("step is not 2. got=%v", step)
	}
}

func TestSteppedSliceStringification(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{
			"myArray[99 : 101 : 2]",
			"(myArray[99:101:2])",
		},
		{
			"myArray[::2]",
			"(myArray[::2])",
		},
		{
			"myArray[4::-1]",
			"(myArray[4::(-1)])",
		},
	}

	for _, tt := range tests {
		exp := parseSteppedSlice(t, tt.input)
		if exp.String() != tt.expected {
			t.Errorf("stringification mismatch. input=%s got=%s want=%s",
				tt.input, exp.String(), tt.expected)
		}
	}
}
