// Copyright (c) 2015-2021 MinIO, Inc.
//
// This file is part of MinIO Object Storage stack
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

package etag

import (
	"testing"
)

// TestParse covers parsing of plain, quoted and multipart ETag strings.
func TestParse(t *testing.T) {
	tests := []struct {
		in         string
		want       ETag
		shouldFail bool
	}{
		// plain singlepart ETag
		{in: "3b83ef96387f14655fc854ddc3c6bd57", want: must("3b83ef96387f14655fc854ddc3c6bd57")},
		// quoted singlepart ETag
		{in: `"3b83ef96387f14655fc854ddc3c6bd57"`, want: must("3b83ef96387f14655fc854ddc3c6bd57")},
		// plain multipart ETag
		{in: "ceb8853ddc5086cc4ab9e149f8f09c88-5", want: must("ceb8853ddc5086cc4ab9e149f8f09c88-5")},
		// quoted multipart ETag
		{in: `"ceb8853ddc5086cc4ab9e149f8f09c88-5"`, want: must("ceb8853ddc5086cc4ab9e149f8f09c88-5")},
		// encrypted (long) ETag
		{in: "20000f00db2d90a7b40782d4cff2b41a7799fc1e7ead25972db65150118dfbe2ba76a3c002da28f85c840cd2001a28a9",
			want: must("20000f00db2d90a7b40782d4cff2b41a7799fc1e7ead25972db65150118dfbe2ba76a3c002da28f85c840cd2001a28a9")},
		// invalid: not hex
		{in: "zz83ef96387f14655fc854ddc3c6bd57", shouldFail: true},
		// invalid: prefix too short for multipart
		{in: "3b83ef96387f14655fc854ddc3c6bd5-1", shouldFail: true},
		// invalid: suffix is not a part number
		{in: "3b83ef96387f14655fc854ddc3c6bd57-", shouldFail: true},
		// invalid: part number not an integer
		{in: "3b83ef96387f14655fc854ddc3c6bd57-x", shouldFail: true},
	}

	for i, test := range tests {
		got, err := Parse(test.in)
		if err != nil && !test.shouldFail {
			t.Fatalf("Test %d: Parse(%q) failed: %v", i, test.in, err)
		}
		if err == nil && test.shouldFail {
			t.Fatalf("Test %d: Parse(%q) should have failed", i, test.in)
		}
		if err == nil && !Equal(got, test.want) {
			t.Fatalf("Test %d: Parse(%q) = %q - want %q", i, test.in, got, test.want)
		}
	}
}

// TestEqual covers equality checks, in particular that a quoted
// and an unquoted representation of the same ETag are equal after
// parsing.
func TestEqual(t *testing.T) {
	plain := must("3b83ef96387f14655fc854ddc3c6bd57")
	quoted, err := Parse(`"3b83ef96387f14655fc854ddc3c6bd57"`)
	if err != nil {
		t.Fatalf("failed to parse quoted ETag: %v", err)
	}
	if !Equal(plain, quoted) {
		t.Fatalf("quoted and unquoted ETags should be equal")
	}
	if !Equal(quoted, plain) {
		t.Fatalf("Equal should be symmetric")
	}

	other := must("7b976cc68452e003eec7cb0eb631a19a")
	if Equal(plain, other) {
		t.Fatalf("different ETags should not be equal")
	}

	multipart := must("ceb8853ddc5086cc4ab9e149f8f09c88-5")
	if Equal(plain, multipart) {
		t.Fatalf("singlepart and multipart ETags should not be equal")
	}
	if !Equal(multipart, must("ceb8853ddc5086cc4ab9e149f8f09c88-5")) {
		t.Fatalf("identical multipart ETags should be equal")
	}
}

// TestMultipart covers building a multipart ETag from a list of
// singlepart ETags. Encrypted and multipart ETags must be ignored.
func TestMultipart(t *testing.T) {
	// empty list
	if got := Multipart(); got != nil {
		t.Fatalf("Multipart() with no parts should return nil, got %q", got)
	}

	// two singlepart ETags
	got := Multipart(
		must("3b83ef96387f14655fc854ddc3c6bd57"),
		must("7b976cc68452e003eec7cb0eb631a19a"),
	)
	want := must("c3d111288bb7b426799549887fb5ff9a-2")
	if !Equal(got, want) {
		t.Fatalf("Multipart(2 parts) = %q - want %q", got, want)
	}
	if !got.IsMultipart() || got.Parts() != 2 {
		t.Fatalf("Multipart(2 parts) should be multipart with 2 parts, got %q", got)
	}

	// one singlepart ETag
	got = Multipart(must("d41d8cd98f00b204e9800998ecf8427e"))
	want = must("59adb24ef3cdbe0297f05b395827453f-1")
	if !Equal(got, want) {
		t.Fatalf("Multipart(1 part) = %q - want %q", got, want)
	}

	// encrypted and multipart ETags must be ignored
	encrypted := must("20000f00db2d90a7b40782d4cff2b41a7799fc1e7ead25972db65150118dfbe2ba76a3c002da28f85c840cd2001a28a9")
	multipart := must("ceb8853ddc5086cc4ab9e149f8f09c88-5")
	got = Multipart(
		must("3b83ef96387f14655fc854ddc3c6bd57"),
		encrypted,
		must("7b976cc68452e003eec7cb0eb631a19a"),
		multipart,
		must("d41d8cd98f00b204e9800998ecf8427e"),
	)
	want = must("49c64a93d4b5fe97b22667067f5552a8-3")
	if !Equal(got, want) {
		t.Fatalf("Multipart with ignored parts = %q - want %q", got, want)
	}
	if got.Parts() != 3 {
		t.Fatalf("Multipart with ignored parts should have 3 parts, got %d", got.Parts())
	}

	// only ignored ETags -> part number 0
	got = Multipart(encrypted, multipart)
	want = must("d41d8cd98f00b204e9800998ecf8427e-0")
	if !Equal(got, want) {
		t.Fatalf("Multipart(only ignored) = %q - want %q", got, want)
	}
}

// TestIsEncrypted covers detection of encrypted ETags based on
// their length.
func TestIsEncrypted(t *testing.T) {
	tests := []struct {
		etag ETag
		want bool
	}{
		{etag: must("3b83ef96387f14655fc854ddc3c6bd57"), want: false},                                                                // 16 bytes
		{etag: must("ceb8853ddc5086cc4ab9e149f8f09c88-5"), want: false},                                                              // multipart, 18 bytes
		{etag: must("7b976cc68452e003eec7cb0eb631a19a-10000"), want: false},                                                          // multipart, 22 bytes
		{etag: must("20000f00db2d90a7b40782d4cff2b41a7799fc1e7ead25972db65150118dfbe2ba76a3c002da28f85c840cd2001a28a9"), want: true}, // 48 bytes
		{etag: must("20000f00f2cc184414bc982927ec56abb7e18426faa205558982e9a8125c1370a9cf5754406e428b3343f21ee1125965"), want: true}, // 48 bytes
	}

	for i, test := range tests {
		if got := test.etag.IsEncrypted(); got != test.want {
			t.Fatalf("Test %d: IsEncrypted(%q) = %v - want %v", i, test.etag, got, test.want)
		}
	}
}

// TestFormat covers formatting ETags for S3: normal ETags are
// returned unmodified, encrypted ETags are truncated to their
// last 16 bytes.
func TestFormat(t *testing.T) {
	// normal singlepart ETag is unchanged
	plain := must("3b83ef96387f14655fc854ddc3c6bd57")
	if got := plain.Format(); !Equal(got, plain) {
		t.Fatalf("Format(plain) = %q - want %q", got, plain)
	}

	// normal multipart ETag is unchanged
	multipart := must("ceb8853ddc5086cc4ab9e149f8f09c88-5")
	if got := multipart.Format(); !Equal(got, multipart) {
		t.Fatalf("Format(multipart) = %q - want %q", got, multipart)
	}

	// encrypted ETag is truncated to the last 16 bytes
	encrypted := must("20000f00db2d90a7b40782d4cff2b41a7799fc1e7ead25972db65150118dfbe2ba76a3c002da28f85c840cd2001a28a9")
	got := encrypted.Format()
	if len(got) != 16 {
		t.Fatalf("Format(encrypted) should be 16 bytes long, got %d", len(got))
	}
	if !Equal(got, encrypted[len(encrypted)-16:]) {
		t.Fatalf("Format(encrypted) = %q - want last 16 bytes %q", got, encrypted[len(encrypted)-16:])
	}
}
