package evaluator

import (
	"strings"
	"testing"

	"github.com/abs-lang/abs/object"
)

// testSteppedSliceArrayValue evaluates input and checks that the result is
// an array with the expected elements.
func testSteppedSliceArrayValue(t *testing.T, input string, expected []interface{}) {
	t.Helper()

	evaluated := testEval(input)
	arr, ok := evaluated.(*object.Array)
	if !ok {
		t.Errorf("object is not Array. got=%T (%s)", evaluated, evaluated.Inspect())
		return
	}
	if len(arr.Elements) != len(expected) {
		t.Errorf("array has wrong length. got=%d want=%d (input=%s)",
			len(arr.Elements), len(expected), input)
		return
	}
	for i, elem := range arr.Elements {
		switch want := expected[i].(type) {
		case int:
			if !testNumberObject(t, elem, float64(want)) {
				t.Errorf("element %d mismatch (input=%s)", i, input)
			}
		case string:
			if !testStringObject(t, elem, want) {
				t.Errorf("element %d mismatch (input=%s)", i, input)
			}
		case nil:
			if !testNullObject(t, elem) {
				t.Errorf("element %d mismatch (input=%s)", i, input)
			}
		}
	}
}

// testSteppedSliceError evaluates input and checks that the result is an
// error whose message starts with expected.
func testSteppedSliceError(t *testing.T, input string, expected string) {
	t.Helper()

	evaluated := testEval(input)
	errObj, ok := evaluated.(*object.Error)
	if !ok {
		t.Errorf("no error object returned. got=%T (%s) (input=%s)",
			evaluated, evaluated.Inspect(), input)
		return
	}
	if !strings.HasPrefix(errObj.Message, expected) {
		t.Errorf("wrong error message. input=%s\nexpected prefix=%q\ngot=%q",
			input, expected, errObj.Message)
	}
}

func TestArraySteppedSliceExpressions(t *testing.T) {
	tests := []struct {
		input    string
		expected []interface{}
	}{
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[0:10:2]",
			[]interface{}{1, 3, 5, 7, 9},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[1:10:3]",
			[]interface{}{2, 5, 8},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[::2]",
			[]interface{}{1, 3, 5, 7, 9},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[:10:2]",
			[]interface{}{1, 3, 5, 7, 9},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[4::2]",
			[]interface{}{5, 7, 9},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[9:0:-1]",
			[]interface{}{10, 9, 8, 7, 6, 5, 4, 3, 2},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[9:0:-2]",
			[]interface{}{10, 8, 6, 4, 2},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[8:2:-3]",
			[]interface{}{9, 6},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[::1]",
			[]interface{}{1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[5:2:1]",
			[]interface{}{},
		},
		{
			"a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; a[0:10:10]",
			[]interface{}{1},
		},
	}

	for _, tt := range tests {
		testSteppedSliceArrayValue(t, tt.input, tt.expected)
	}
}

func TestStringSteppedSliceExpressions(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{
			`"abcdefghij"[0:10:2]`,
			"acegi",
		},
		{
			`"abcdefghij"[1:10:3]`,
			"bdfh",
		},
		{
			`"abcdefghij"[::2]`,
			"acegi",
		},
		{
			`"abcdefghij"[:10:2]`,
			"acegi",
		},
		{
			`"abcdefghij"[4::2]`,
			"efi",
		},
		{
			`"abcdefghij"[9:0:-1]`,
			"jihgfedcb",
		},
		{
			`"abcdefghij"[9:0:-2]`,
			"jhfdb",
		},
		{
			`"abcdefghij"[8:2:-3]`,
			"if",
		},
		{
			`"abcdefghij"[::1]`,
			"abcdefghij",
		},
		{
			`"abcdefghij"[5:2:1]`,
			"",
		},
	}

	for _, tt := range tests {
		evaluated := testEval(tt.input)
		if !testStringObject(t, evaluated, tt.expected) {
			t.Errorf("string slice mismatch. input=%s", tt.input)
		}
	}
}

func TestStringSteppedSliceUnicode(t *testing.T) {
	// "héllo wörld" is 11 runes but 13 bytes; slicing must be rune-based
	tests := []struct {
		input    string
		expected string
	}{
		{
			`"héllo wörld"[0:11:2]`,
			"hlowrd",
		},
		{
			`"héllo wörld"[10:0:-2]`,
			"drwol",
		},
		{
			`"héllo wörld"[::2]`,
			"hlowrd",
		},
	}

	for _, tt := range tests {
		evaluated := testEval(tt.input)
		if !testStringObject(t, evaluated, tt.expected) {
			t.Errorf("unicode string slice mismatch. input=%s", tt.input)
		}
	}
}

func TestSteppedSliceErrors(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{
			"a = [1, 2, 3]; a[0:3:0]",
			"slice step cannot be 0",
		},
		{
			`"abc"[0:3:0]`,
			"slice step cannot be 0",
		},
		{
			`"abc"[::0]`,
			"slice step cannot be 0",
		},
		{
			`[1, 2, 3]["a"]`,
			`index operator not supported: "a" on ARRAY`,
		},
		{
			`"abc"[{}]`,
			`index operator not supported: {} on STRING`,
		},
		{
			`"abc"[0:"x"]`,
			`index ranges can only be numerical: got "x" (type STRING)`,
		},
		{
			`"abc"[0:3:"x"]`,
			`index ranges can only be numerical: got "x" (type STRING)`,
		},
		{
			`[1, 2, 3][0:3:{}]`,
			`index ranges can only be numerical: got {} (type HASH)`,
		},
	}

	for _, tt := range tests {
		testSteppedSliceError(t, tt.input, tt.expected)
	}
}

func TestArraySteppedSliceAssignment(t *testing.T) {
	tests := []struct {
		input    string
		expected []interface{}
	}{
		{
			"a = [1, 2, 3, 4, 5, 6]; a[1:5:2] = [10, 20]; a",
			[]interface{}{1, 10, 3, 20, 5, 6},
		},
		{
			"a = [1, 2, 3, 4, 5, 6]; a[0:6:2] = [10, 20, 30]; a",
			[]interface{}{10, 2, 30, 4, 30, 6},
		},
		{
			"a = [1, 2, 3, 4, 5, 6]; a[1:5:2] = 99; a",
			[]interface{}{1, 99, 3, 99, 5, 6},
		},
		{
			"a = [1, 2, 3, 4, 5, 6]; a[0:4] = [10, 20, 30, 40]; a",
			[]interface{}{10, 20, 30, 40, 5, 6},
		},
		{
			"a = [1, 2, 3, 4, 5, 6]; a[0:4] = 7; a",
			[]interface{}{7, 7, 7, 7, 5, 6},
		},
		{
			"a = [1, 2, 3, 4, 5, 6]; a[5:1:-2] = [10, 20]; a",
			[]interface{}{1, 2, 3, 20, 5, 10},
		},
	}

	for _, tt := range tests {
		testSteppedSliceArrayValue(t, tt.input, tt.expected)
	}
}

func TestArraySteppedSliceAssignmentErrors(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{
			"a = [1, 2, 3, 4, 5, 6]; a[1:5:2] = [10]; a",
			"range assignment size mismatch: target=2 value=1",
		},
		{
			"a = [1, 2, 3, 4, 5, 6]; a[1:5:2] = [10, 20, 30]; a",
			"range assignment size mismatch: target=2 value=3",
		},
		{
			"a = [1, 2, 3, 4, 5, 6]; a[5:5] = [10]; a",
			"range assignment size mismatch: target=0 value=1",
		},
	}

	for _, tt := range tests {
		testSteppedSliceError(t, tt.input, tt.expected)
	}
}

func TestStringSteppedSliceAssignment(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{
			`s = "abcdef"; s[1:5:2] = "XY"; s`,
			"aXcYef",
		},
		{
			`s = "abcdef"; s[0:6:2] = "XYZ"; s`,
			"XbYdZe",
		},
		{
			`s = "abcdef"; s[1:5:2] = "X"; s`,
			"aXcXef",
		},
		{
			`s = "abcdef"; s[0:4] = "WXYZ"; s`,
			"WXYZef",
		},
		{
			`s = "abcdef"; s[0:4] = "W"; s`,
			"WWWWef",
		},
		{
			`s = "abcdef"; s[5:1:-2] = "XY"; s`,
			"abcYeX",
		},
		{
			`s = "abcdef"; s[2] = "X"; s`,
			"abXdef",
		},
	}

	for _, tt := range tests {
		evaluated := testEval(tt.input)
		if !testStringObject(t, evaluated, tt.expected) {
			t.Errorf("string assignment mismatch. input=%s", tt.input)
		}
	}
}

func TestStringSteppedSliceAssignmentUnicode(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{
			`s = "héllo"; s[1:5:2] = "XY"; s`,
			"hXlYo",
		},
		{
			`s = "héllo"; s[2] = "X"; s`,
			"héXlo",
		},
	}

	for _, tt := range tests {
		evaluated := testEval(tt.input)
		if !testStringObject(t, evaluated, tt.expected) {
			t.Errorf("unicode string assignment mismatch. input=%s", tt.input)
		}
	}
}

func TestStringSteppedSliceAssignmentErrors(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{
			`s = "abcdef"; s[1:5:2] = "XYZ"; s`,
			"range assignment size mismatch: target=2 value=3",
		},
		{
			`s = "abcdef"; s[5:5] = "X"; s`,
			"range assignment size mismatch: target=0 value=1",
		},
		{
			`s = "abcdef"; s[1:5:2] = 10; s`,
			"range assignment expects STRING value, got NUMBER",
		},
		{
			`s = "abcdef"; s[2] = "XY"; s`,
			"index assignment expects single-character STRING value, got 2 characters",
		},
	}

	for _, tt := range tests {
		testSteppedSliceError(t, tt.input, tt.expected)
	}
}
