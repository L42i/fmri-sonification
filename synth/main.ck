53 => global int N;

// NOTE: un-@import-able, see https://chuck.stanford.edu/doc/examples/import/Foo.ck
[
  "osc.ck",
  "granular.ck"
] @=> string files[];

for (string file : files) me.dir() + file => Machine.add;