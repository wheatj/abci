package proxy

import (
	"sync"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	abcicli "github.com/tendermint/abci/client"
	"github.com/tendermint/abci/example/counter"
	"github.com/tendermint/abci/types"
)

func TestProxyEcho(t *testing.T) {
	assert := assert.New(t)
	require := require.New(t)

	prefix := []byte("echo")
	next := counter.NewCounterApplication(false)

	// setup code
	mtx := sync.Mutex{}
	client := abcicli.NewLocalClient(&mtx, next)
	proxy := NewProxyApp(client, prefix)

	// make sure the counter works normally...
	res := proxy.DeliverTx([]byte("12345"))
	require.False(res.IsErr(), "%+v", res)

	cres := proxy.Commit()
	require.False(cres.IsErr(), "%+v", cres)

	query := types.RequestQuery{Path: "tx"}
	qres := proxy.Query(query)
	require.True(qres.GetCode().IsOK(), "%+v", qres)
	assert.Equal([]byte("1"), qres.GetValue())

	// now, let's see how the echo command works...
	res = proxy.DeliverTx([]byte("echohello, world!"))
	require.False(res.IsErr(), "%+v", res)
	require.Equal("Echo: hello, world!", res.Log, "%+v", res)

	// commit and query shouldn't change anything, as counter app wasn't called
	cres = proxy.Commit()
	require.False(cres.IsErr(), "%+v", cres)

	qres = proxy.Query(query)
	require.True(qres.GetCode().IsOK(), "%+v", qres)
	assert.Equal([]byte("1"), qres.GetValue())
}
